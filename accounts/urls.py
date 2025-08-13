from django.urls import path
from . import views




urlpatterns = [

    path('register/',views.register,name='register'),
    path('login/',views.login,name = 'login'),
    path('logout/',views.logout, name = 'logout'),
    path('verify-account/',views.verify_account, name= 'verify_account')
              
              ]