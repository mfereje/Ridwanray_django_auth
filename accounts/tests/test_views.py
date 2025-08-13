

from django.test.client import Client
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from accounts.models import PendingUser
from django.contrib.messages import get_messages


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


def test_register_user_duplicate_email():
    ''''''

def test_verify_account_valid_code():
    ''''''

def test_verify_account_invalid_code():
    ''''''

def test_login_valid_credentials():
    ''''''

def test_login_invalid_credentials():
    ''''''
