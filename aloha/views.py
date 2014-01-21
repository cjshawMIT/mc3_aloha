import json
import logging
import pdb

from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

def create_user(request):
    if request.method == 'POST':
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        passwd = request.POST['passwd']

        if not User.objects.filter(email = email).exists():
            user = User.objects.create_user(email, email, passwd)
            user.is_active = True
            if not fname:
                user.first_name = email.split('@')[0]
            else:
                user.first_name = fname
            user.last_name = lname
            user.save()
            user = authenticate(username=email, password=passwd)
            login(request, user)
            return HttpResponseRedirect(reverse('aloha:dashboard'))
        else:
            return render(request, 'aloha/register.html',
                    {'error' : 'E-mail already exists. Please try again.'})
    return HttpResponseRedirect(reverse('aloha:register'))

@login_required
@user_passes_test(lambda u: u.is_active)
def dashboard(request):
    """
    User dashboard to edit books?
    """
    cur_user = request.user
    return render(request, 'aloha/dashboard.html')

def index(request):
    redirect = request.GET.get('next')
    if not redirect:
        redirect = reverse('aloha:dashboard')
    return render(request, 'aloha/index.html', {
        'next':redirect,})

def login_page(request):
    """
    Log in users, according to
    https://docs.djangoproject.com/en/dev/topics/auth/default/#auth-web-requests
    """
    username = request.POST['email']
    password = request.POST['passwd']
    redirect_url = request.POST['next']
    user = authenticate(username = username, password = password)
    if user is not None:
        if user.is_active:
            login(request, user)
            return HttpResponseRedirect(redirect_url)
        else:
            state = "Your account is not active."
    else:
        state = "Incorrect username and/or password."
    return render(request, 'aloha/index.html', {
        'state' : state, 'next': redirect_url})

def logout_page(request):
    """
    Log users out and re-direct them back to index
     """
    logout(request)
    return HttpResponseRedirect(reverse('aloha:index'))

def privacy(request):
    """
    Redirect to the site's Privacy Policy
    """
    return render(request, 'aloha/privacy.html')

def register(request):
    """
    To render the register page
    """
    return render(request, 'aloha/register.html')

def tos(request):
    """
    Redirect to the site's Terms of Service
    """
    return render(request, 'aloha/tos.html')