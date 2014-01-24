import json
import logging
import pdb

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test

from .aloha_utils import *

from bs4 import BeautifulSoup

# TODO: add in email verification for registration:
# http://stackoverflow.com/questions/5495317/implementation-of-e-mail-verification-in-django
# http://stackoverflow.com/questions/1325983/django-send-email-in-html-with-django-registration

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
    return render(request, 'aloha/dashboard.html')

@login_required
@user_passes_test(lambda u: u.is_active)
def get_key(request):
    key = ''
    host = request.GET['host']
    try:
        key = request_key_from_handcar(request.user, host)
    except Exception as ex:
        log_error('views.get_key()', ex)
    finally:
        return HttpResponse(key)

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

@login_required
@user_passes_test(lambda u: u.is_active)
def sandbox(request):
    with open(settings.PROJECT_PATH + '/../templates/sandbox/index.html') as f:
        page = BeautifulSoup(f)
        return HttpResponse(page.html)
    # return render(request, 'sandbox/index.html')

def tos(request):
    """
    Redirect to the site's Terms of Service
    """
    return render(request, 'aloha/tos.html')