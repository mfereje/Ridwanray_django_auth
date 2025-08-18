from datetime import datetime
from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from accounts.models import PendingUser, Token, TokenType,User
from django.contrib.messages import get_messages
from django.contrib.auth import get_user

def test_register_user(db,client:Client):
    url=reverse('register')
    request_data = {
        'email': 'abc@gmail.com',
        'password' : 123456
    }
    response = client.post(url,request_data)
    assert response.status_code == 200

    pending_user = PendingUser.objects.filter(
        email=request_data['email'],
        
    ).first()
    assert pending_user
    assert check_password(request_data['password'], pending_user.password)

    messages=list(get_messages(response.wsgi_request))

    assert len(messages) == 1
    assert messages[0].level_tag == 'success'
    assert "The Verification code sent to" in str(messages[0])




    ''''''


def test_register_user_duplicate_email(client:Client,user_instance):
    url=reverse('register')
    request_data={
        'email':user_instance.email,
        'password':'abc'
    }
    response=client.post(url,request_data)
    messages=list(get_messages(response.wsgi_request))
    assert response.status_code==302
    assert response.url == reverse('register')

    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert "Email exists in the platform" in str(messages[0])




    ''''''

def test_verify_account_valid_code(db,client:Client):
    pending_user=PendingUser.objects.create(
        email="abc@gmail.com",
        verification_code="55555",
        password="randompass"
    )
    url=reverse('verify_account')
    request_data={
        'email':pending_user.email,
        'code': pending_user.verification_code
    }
    response=client.post(url,request_data)
    assert response.status_code == 302
    assert response.url == reverse('home')

    user=get_user(response.wsgi_request)
    assert user.is_authenticated

    ''''''

def test_verify_account_invalid_code(db,client:Client):
    pending_user=PendingUser.objects.create(
        email="abc@gmail.com",
        verification_code="55555",
        password="randompass"
    )
    url=reverse('verify_account')
    request_data={
        'email':pending_user.email,
        'code': "invalid code"
    }
    response=client.post(url,request_data)
    assert response.status_code == 400
    assert User.objects.count() == 0

    messages=list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
   



def test_login_valid_credentials(db,client:Client,user_instance,auth_user_password):
    request_data = {
        'email':user_instance.email,
        'password':auth_user_password
    }
    url = reverse('login')
    response = client.post(url, request_data)

    assert response.status_code == 302
    assert response.url == reverse('home')
    messages=list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'success'
   

def test_login_invalid_credentials(client:Client,user_instance,):
    request_data = {
        'email':user_instance.email,
        'password':"randominvalidpass"
    }
    url = reverse('login')
    response = client.post(url, request_data)

    assert response.status_code == 302
    assert response.url == reverse('login')
    messages=list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert "Invalid credentials" in str(messages[0])

def test_initiate_password_reset_using_register_email(client : Client, user_instance):
    url = reverse("reset_password_via_email")
    request_data = {'email' : user_instance.email}
    response = client.post(url , request_data)
    assert response.status_code == 302
    assert Token.objects.get(user__email = request_data["email"],token_type = TokenType.PASSWORD_RESET)
    messages=list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'success'
    assert str(messages[0]) == "Reset link sent to your email"


def test_initiate_password_reset_using_unregister_email(client : Client,db):
    url = reverse("reset_password_via_email")
    request_data = {'email' : "notregistered@gmail.com"}
    response = client.post(url , request_data)
    assert response.status_code == 302
    assert not Token.objects.filter(user__email = request_data["email"],token_type = TokenType.PASSWORD_RESET).first()
    messages=list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert str(messages[0]) == "Email not found"


def test_set_new_password_using_valid_reset_token(client : Client, user_instance,db):
    url = reverse("set_new_password")
    token_reset = Token.objects.create(user = user_instance, token_type = TokenType.PASSWORD_RESET,token = "abcd", created_at = datetime.now())
    request_data = {
        "password1" : "12345",
        "password2" : "12345",
        "email" : user_instance.email,
        "token" : token_reset.token
    }

    response = client.post(url, request_data)
    messages=list(get_messages(response.wsgi_request))
    assert response.status_code == 302
    assert response.url == reverse("login")

    # assert len(messages) == 1
    # assert messages[0].level_tag == 'success'
    # assert str(messages[0]) == "Password Changed"

    assert Token.objects.count() == 0
    user_instance.refresh_from_db()

    assert user_instance.check_password(request_data['password1'])
    messages=list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'success'
    assert str(messages[0]) == "Password changed"




def test_set_new_password_using_invalid_reset_token(client : Client, user_instance):
    url = reverse("set_new_password")
    token_reset = Token.objects.create(user = user_instance, token_type = TokenType.PASSWORD_RESET,token = "abcd", created_at = datetime.now())
    request_data = {
        "password1" : "12345",
        "password2" : "12345",
        "email" : user_instance.email,
        "token" : "fakeinvalidtoken"
    }

    response = client.post(url, request_data)
  
    assert response.url == reverse('reset_password_via_email')
    assert Token.objects.count() == 1
    

  
    messages=list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert messages[0].level_tag == 'error'
    assert str(messages[0]) == "invalid or expired reset link"
