from django.urls import path
from .views import *

urlpatterns = [

    path('register/',  account_registration, name='register'),
    path('login/', Login_View, name='login'),
    path('logout', logout_view, name='logout'),
    path('activate/<uidb64>/<token>/',activate_email, name='activate'),
]
