#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django.urls import path
from .views import login, login_for_modal, logout, user_info, register, change_nickname, bind_email, \
    send_verification_code, change_password, forget_password

urlpatterns = [
    path('login/', login, name='login'),
    path('login_for_modal/', login_for_modal, name='login_for_modal'),
    path('logout/', logout, name='logout'),
    path('user_info/', user_info, name='user_info'),
    path('register/', register, name='register'),
    path('change_nickname/', change_nickname, name='change_nickname'),
    path('bind_email/', bind_email, name='bind_email'),
    path('send_verification_code/', send_verification_code, name='send_verification_code'),
    path('change_password/', change_password, name='change_password'),
    path('forget_password/', forget_password, name='forget_password'),
]
