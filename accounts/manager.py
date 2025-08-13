from django.contrib.auth.base_user import BaseUserManager


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is unique identifier
    """

    def create_user(self,email,password, **extra_fields):
        """
        creaate a user with a given email and password
        """

        if not email:
            raise ValueError("Email must be set")
        
        user=self.model(email=email)
        user.user.set_password(password)
        user.save()
        return user
    

    def create_superuser(self,email,password,**extra_fields):

        """
        create and save superuser with the given email and password
        """
        extra_field.setdefault("is_staff",True)
        extra_field.setdefault("is_superuser",True)

        if extra_field.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_field.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True")
        user=user = self.create_user(email, password,extra_fields)
        user.save()
        return user
        
        

    