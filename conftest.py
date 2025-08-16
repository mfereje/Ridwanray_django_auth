from django.test.client import Client
from accounts.models import User
import pytest
from django.contrib.auth.hashers import make_password
@pytest.fixture
def client():
    return Client()

@pytest.fixture
def user_instance(db):
    return User.objects.create(
        email="random@gmail.com",
        password=make_password("abcd")
    )
@pytest.fixture
def auth_user_password():
    '''returns the password needed for authentication'''
    return 'abcd'