from django.shortcuts import redirect, render
from django.http import HttpRequest
from django.contrib import messages,auth
from django.utils.crypto import get_random_string
from .models import PendingUser
from django.contrib.auth.hashers import make_password
from datetime import datetime,timezone
from common.tasks import send_email
from .models import User,Token,TokenType
from django.contrib.auth import get_user_model
from .decorators import redirect_authenticated_user
# Create your views here.
def home(request:HttpRequest):
    return render(request,'home.html')

@redirect_authenticated_user
def login(request:HttpRequest):
    if request.method == 'POST':
        email:str = request.POST.get('email')
        password:str = request.POST.get('password')

        user = auth.authenticate(request,email = email, password = password)

        if user is not None:
            auth.login(request, user)
            messages.success(request,'You are now logged in')
            return redirect('home')
        else:
            messages.error(request,"Invalid credentials")
            return redirect('login')

    else:
       return render(request,"login.html")

def logout(request:HttpRequest):
    auth.logout(request)
    messages.success(request,'You are now logged out')
    return redirect('home')



def register(request : HttpRequest):

    if request.method == 'POST':

        email:str=request.POST['email']
        password:str=request.POST['password']
        cleaned_email=email.lower()

        if User.objects.filter(email=cleaned_email).exists():
            messages.error(request,'Email exists in the platform')
            return redirect('register')
        else: 
            verification_code=get_random_string(10)
            PendingUser.objects.update_or_create(
                email=cleaned_email,
                defaults={
                    "password":make_password(password),
                    "verification_code": verification_code,
                    "created_at":datetime.now(timezone.utc)
                
            })

            #sent email
            send_email.delay(
                "Verify Your Account",
                [cleaned_email],
                "emails/email_verification_template.html",
                context={'code':verification_code}
            )

            messages.success(request,f"The Verification code sent to {cleaned_email}")
            return render(request,"verify_account.html",{'email':cleaned_email})
            




    else:
        return render(request, 'register.html')


def verify_account(request:HttpRequest):
    if request.method == 'POST':
        code : str=request.POST['code']
        email: str=request.POST['email']
        pending_user:PendingUser =PendingUser.objects.filter(
            verification_code = code,
            email = email
        ).first()
        if pending_user and pending_user.is_valid():
            user = User.objects.create(
                email = pending_user.email,
                password=pending_user.password
            )
            pending_user.delete()
            auth.login(request,user)
            messages.success(request,"Account verified. You are now logged in")
            return redirect("home")
        else:
            messages.error(request,"Invalid or expired verification code")
            return render(request, 'verify_account.html',{'email':email}, status=400)

def send_password_reset_link(request : HttpRequest):
    if request.method == 'POST':
        email:str = request.POST.get('email',"")
        user = get_user_model().objects.filter(email = email.lower()).first()
        if user:
           token, _ = Token.objects.update_or_create(
                user = user,
                token_type = TokenType.PASSWORD_RESET,
                defaults={
                    'token' : get_random_string(20),
                    'created_at' : datetime.now(timezone.utc) 
                }
            )
           email_data = {
               'email' : email,
               'token' : token.token
           }
           send_email.delay(
               "Your Password Reset Link",
            [email],
               "emails/password_reset_template.html",
               email_data
           )

           messages.success(request,"Reset link sent to your email")
           return redirect('reset_password_via_email')

        else:
            messages.error(request,"Email not found")
            return redirect('reset_password_via_email')

    else:
        return render(request, 'forgot_password.html')
    
def verify_password_reset_link(request:HttpRequest):
    email = request.GET.get("email")
    reset_token = request.GET.get('token')

    token : Token = Token.objects.filter(
        user__email=email, token = reset_token, token_type = TokenType.PASSWORD_RESET
    ).first()

    if not token or not token.is_valid():
        messages.error(request,"invalid or expired reset link")
        return redirect('reset_password_via_email')
    
    return render(request, 'set_new_password_using_reset_token.html',context={'email' : email,'token' : reset_token})



def reset_password_using_reset_link(request : HttpRequest):
    ''' set a new password given the token sent to a user email '''
    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        email  = request.POST.get('email')
        reset_token = request.POST.get('token')

        if password1 != password2:
            messages.error(request, "Password not match")
            return render(request,'set_new_password_using_reset_token.html',context={'email' : email,'token' : reset_token})
        
    token : Token = Token.objects.filter(
        user__email=email, token = reset_token, token_type = TokenType.PASSWORD_RESET
    ).first()

    if not token or not token.is_valid():
        messages.error(request,"invalid or expired reset link")
        return redirect('reset_password_via_email')
    token.reset_user_password(password1)
    token.delete()
    messages.success(request,"Password changed")
    return redirect('login')