from django.shortcuts import render, get_object_or_404,redirect

# Create your views here.
from django.apps import apps
from django.http import Http404, HttpRequest, HttpResponse
# from vwh_capital.website.models import *
from django.contrib.auth.tokens import default_token_generator
# Used to send mail from within Django
from django.core.mail import send_mail
from .forms import *
from .models import *
from django.db import transaction
from django.urls import reverse
from django.apps import apps
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.core import serializers


@transaction.atomic
def register(request):
    context = {}
    # Just display the registration form if this is a GET request.
    if request.method == 'GET':
        context['form'] = RegistrationForm()
        return render(request, 'website/signup.html', context)

    # Creates a bound form from the request POST parameters and makes the
    # form available in the request context dictionary.
    form = RegistrationForm(request.POST)
    context['form'] = form

    # Validates the form.
    if not form.is_valid():
        return render(request, 'website/signup.html', context)

    # At this point, the form data is valid.  Register and login the user.
    new_user = User.objects.create_user(username=form.cleaned_data['username'],
                                        password=form.cleaned_data['password1'],
                                        email=form.cleaned_data['email'],
                                        first_name=form.cleaned_data['first_name'],
                                        last_name=form.cleaned_data['last_name'])
    # new_user.is_active = False
    new_user.save()

    new_profile = Profile(user=new_user,
                          longitude=form.cleaned_data['longitude'],
                          latitude=form.cleaned_data['latitude']
                          )

    new_profile.save()

    # Generate a one-time use token and an email message body
    token = default_token_generator.make_token(new_user)

    email_body = """
        Please click the link below to verify your email address and
        complete the registration of your account:
        http://{host}{path}
        """.format(host=request.get_host(),
                   path=reverse('confirm', args=(new_user.username, token)))

    send_mail(subject="Verify your email address",
              message=email_body,
              from_email="yuzhe.yin@vwhcapital.com",
              recipient_list=[new_user.email])

    context['email'] = form.cleaned_data['email']

    return render(request, 'website/confirmation.html', context)


@transaction.atomic
def confirm_registration(request, username, token):
    user = get_object_or_404(User, username=username)

    # Send 404 error if token is invalid
    if not default_token_generator.check_token(user, token):
        raise Http404

    # Otherwise token was valid, activate the user.
    user.is_active = True
    user.save()
    login(request, user)
    return render(request, 'website/index.html', {})


@login_required
def contact(request):
    if request.method == 'GET':
        return render(request, 'website/contact.html')
    userName=request.user.username
    email_body = """
    User {user} sent you an email, here is the message:
    {message}
    and user's email: {email}
    """.format(user=request.user,
               message=request.POST['message'],
               email=request.user.email)

    send_mail(subject="Message from customer "+userName,
              message=email_body,
              from_email="yuzhe.yin@vwhcapital.com",
              recipient_list=["yuzhe.yin@vwhcapital.com"])
    context={}
    context['success'] = "Your email has been successfully sent! We will contact you soon!"
    return render(request, 'website/contact.html', context)


def login(request):
    if request.method == 'GET':
        return render(request, 'website/login.html')
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return render(request, 'website/index.html')
    else:
        errors = {'Invalid username or password, please try again'}
        return render(request, 'website/login.html', {'errors': errors})


def properties(request):
    return render(request, 'website/properties.html')


def details(request):
    return render(request, 'website/details.html')


def favourite(request):
    return render(request, 'website/favorite.html')


def home(request):
    return render(request, 'website/index.html')


def favorite(request):
    return render(request, 'website/favorite.html')