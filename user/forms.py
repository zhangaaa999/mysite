#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from django import forms
from django.contrib import auth
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username_or_email = forms.CharField(label='用户名',
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': '请输入用户名或邮箱'}))
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))

    def clean(self):
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username_or_email, password=password)
        if user is None:
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)
                if user is not None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('用户名或密码错误')
        else:
            self.cleaned_data['user'] = user

        return self.cleaned_data


class RegForm(forms.Form):
    username = forms.CharField(label='用户名',
                               max_length=30,
                               min_length=3,
                               widget=forms.TextInput(
                                   attrs={'class': 'form-control', 'placeholder': '请输入用户名'}))
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': '请输入邮箱地址'}))
    verification_code = forms.CharField(label='验证码',
                                        required=False,
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    password = forms.CharField(label='密码',
                               max_length=30,
                               min_length=3,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': '请输入密码'}))
    password_again = forms.CharField(label='确认密码',
                                     max_length=30,
                                     min_length=3,
                                     widget=forms.PasswordInput(
                                         attrs={'class': 'form-control', 'placeholder': '请再次输入密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        forms.Form.__init__(self, *args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_verification_code(self):
        form_verification_code = self.cleaned_data['verification_code']
        email_verification_code = self.request.session.get('email_verification_code', '')
        if not (email_verification_code != '' and email_verification_code == form_verification_code):
            raise forms.ValidationError('验证码错误')
        return form_verification_code

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again


class NicknameForm(forms.Form):
    new_nickname = forms.CharField(label='昵称',
                                   max_length=20,
                                   widget=forms.TextInput(
                                       attrs={'class': 'form-control', 'placeholder': '请输入昵称'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        forms.Form.__init__(self, *args, **kwargs)

    def clean(self):
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError("用户没有登录")
        return self.cleaned_data

    def clean_new_nickname(self):
        new_nickname = self.cleaned_data.get('new_nickname', '').strip()
        if new_nickname == "":
            raise forms.ValidationError("新的昵称不能为空")
        return new_nickname


class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮箱',
                             widget=forms.EmailInput(
                                 attrs={'class': 'form-control', 'placeholder': '请输入正确邮箱地址'}))
    verification_code = forms.CharField(label='验证码',
                                        required=False,
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        forms.Form.__init__(self, *args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError("用户没有登录")

        # 判断用户是否绑定邮箱
        if self.request.user.email != "":
            raise forms.ValidationError("你已经绑定了邮箱")

        # 判断验证码
        code = self.request.session.get('email_verification_code', '')
        verification_code = self.cleaned_data.get('verification_code', '')
        if not (code != "" and code == verification_code):
            raise forms.ValidationError("验证码不正确")

        return self.cleaned_data

    def clean_new_nickname(self):
        new_nickname = self.cleaned_data.get('new_nickname', '').strip()
        if new_nickname == "":
            raise forms.ValidationError("新的昵称不能为空")
        return new_nickname


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='旧密码',
                                   max_length=30,
                                   min_length=3,
                                   widget=forms.PasswordInput(
                                       attrs={'class': 'form-control', 'placeholder': '请输入旧密码'}))
    new_password = forms.CharField(label='新密码',
                                   max_length=30,
                                   min_length=3,
                                   widget=forms.PasswordInput(
                                       attrs={'class': 'form-control', 'placeholder': '请输入新密码'}))

    new_password_again = forms.CharField(label='确认新密码',
                                         max_length=30,
                                         min_length=3,
                                         widget=forms.PasswordInput(
                                             attrs={'class': 'form-control', 'placeholder': '请再次输入新密码'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        forms.Form.__init__(self, *args, **kwargs)

    def clean(self):
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError("用户没有登录")
        return self.cleaned_data

    def clean_old_password(self):
        old_password = self.cleaned_data['old_password']
        # if auth.authenticate(username=self.user.username, password=old_password) is None:
        if not self.user.check_password(old_password):
            raise forms.ValidationError("旧密码错误")
        return old_password

    def clean_new_password_again(self):
        new_password = self.cleaned_data['new_password']
        new_password_again = self.cleaned_data['new_password_again']
        if new_password != new_password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return new_password_again


class ForgetPasswordForm(forms.Form):
    email = forms.EmailField(label='邮箱', widget=forms.EmailInput(
        attrs={'class': 'form-control', 'placeholder': '请输入邮箱地址'}))
    verification_code = forms.CharField(label='验证码',
                                        required=False,
                                        widget=forms.TextInput(
                                            attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    password = forms.CharField(label='密码',
                               max_length=30,
                               min_length=3,
                               widget=forms.PasswordInput(
                                   attrs={'class': 'form-control', 'placeholder': '请输入密码'}))
    password_again = forms.CharField(label='确认密码',
                                     max_length=30,
                                     min_length=3,
                                     widget=forms.PasswordInput(
                                         attrs={'class': 'form-control', 'placeholder': '请再次输入密码'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        forms.Form.__init__(self, *args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('该邮箱不存在')
        user = User.objects.get(email=email)
        self.cleaned_data['user'] = user
        return email

    def clean_verification_code(self):
        form_verification_code = self.cleaned_data['verification_code']
        email_verification_code = self.request.session.get('email_verification_code', '')
        if not (email_verification_code != '' and email_verification_code == form_verification_code):
            raise forms.ValidationError('验证码错误')
        return form_verification_code

    def clean_password_again(self):
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again
