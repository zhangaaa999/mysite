import time
import string
import random
from django.http import JsonResponse
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.urls import reverse
from .forms import LoginForm, RegForm, NicknameForm, BindEmailForm, ChangePasswordForm, ForgetPasswordForm
from .models import Profile


def login(request):
    referer_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            return redirect(referer_to)
    else:
        login_form = LoginForm()
    context = dict()

    context['form'] = login_form
    context['form_title'] = '登录'
    context['form_submit'] = '登录'
    context['return_back_url'] = referer_to
    return render(request, 'user/login.html', context)


def login_for_modal(request):
    data = dict()
    login_form = LoginForm(request.POST)
    if login_form.is_valid():
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def register(request):
    referer_to = request.GET.get('from', reverse('home'))
    if request.method == 'POST':
        reg_form = RegForm(request.POST, request=request)
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            del request.session['email_verification_code']
            auth.login(request, user)
            return redirect(referer_to)
    else:
        reg_form = RegForm()
    context = dict()
    context['form'] = reg_form
    context['form_title'] = '注册'
    context['form_submit'] = '注册'
    context['return_back_url'] = referer_to

    return render(request, 'register.html', context)


def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))


def user_info(request):
    return render(request, 'user_info.html')


def change_nickname(request):
    referer_to = request.GET.get('from', reverse('user_info'))
    if request.method == "POST":
        nickname_form = NicknameForm(request.POST, user=request.user)
        if nickname_form.is_valid():
            new_nickname = nickname_form.cleaned_data['new_nickname']
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.nickname = new_nickname
            profile.save()
            return redirect(referer_to)
    else:
        nickname_form = NicknameForm()
    context = dict()
    context['form'] = nickname_form
    context['form_title'] = '修改昵称'
    context['form_submit'] = '确认'
    context['return_back_url'] = referer_to
    return render(request, 'form.html', context)


def bind_email(request):
    referer_to = request.GET.get('from', reverse('user_info'))
    if request.method == "POST":
        print("bind_email POST 被执行")
        bind_email_form = BindEmailForm(request.POST, request=request)
        if bind_email_form.is_valid():
            email = bind_email_form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            del request.session['email_verification_code']
            return redirect(referer_to)
    else:
        bind_email_form = BindEmailForm()
    context = dict()
    context['form'] = bind_email_form
    context['form_title'] = '绑定邮箱'
    context['form_submit'] = '绑定'
    context['return_back_url'] = referer_to
    return render(request, 'user/bind_email.html', context)


def send_verification_code(request):
    email = request.GET.get('email', '')
    data = {}

    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        now = int(time.time())
        send_code_time = request.session.get('send_code_time', 0)
        if now - send_code_time < 30:
            data['status'] = 'ERROR'
        else:
            request.session['email_verification_code'] = code
            request.session['send_code_time'] = now

            # 发送邮件
            send_mail(
                '绑定邮箱',
                '验证码：%s' % code,
                '497130864@qq.com',
                [email],
                fail_silently=False,
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)


def change_password(request):
    referer_to = request.GET.get('from', reverse('user_info'))
    if request.method == "POST":
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)
            user.save()
            auth.login(request, user)
            return redirect(referer_to)
    else:
        form = ChangePasswordForm()
    context = dict()
    context['form'] = form
    context['form_title'] = '修改密码'
    context['form_submit'] = '确认修改'
    context['return_back_url'] = referer_to
    return render(request, 'form.html', context)


def forget_password(request):
    referer_to = request.GET.get('from', reverse('home'))
    if request.method == "POST":
        form = ForgetPasswordForm(request.POST, request=request)
        if form.is_valid():
            user = form.cleaned_data['user']
            password = form.cleaned_data['password']
            user.set_password(password)
            user.save()
            auth.login(request, user)
            del request.session['email_verification_code']
            return redirect(reverse('home'))
    else:
        form = ForgetPasswordForm()
    context = dict()
    context['form'] = form
    context['form_title'] = '重置密码'
    context['form_submit'] = '确认重置'
    context['return_back_url'] = referer_to
    return render(request, 'user/forget_password.html', context)
