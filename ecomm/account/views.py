from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer 

# to get the current url of the page/site -> will be used for acoount activation link through mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.urls import NoReverseMatch, reverse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError

# mail imports
from django.core.mail import send_mail, EmailMultiAlternatives, EmailMessage
from django.core.mail import BadHeaderError, send_mail
from django.core import mail
from django.conf import settings

# token from utils.py
from .utils import TokenGenerator, genrate_token

# Email Threding imports
import threading

# This Treading class will make email processing fast
class EmailThread(threading.Thread):
    def __init__(self, email_message):
        super(EmailThread, self).__init__()
        self.email_message = email_message
    def run(self):
        self.email_message.send()

# Create your views here.
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index-page')
    elif request.method == "POST":
        firstname = request.POST['first_name']
        lastname = request.POST['last_name']
        # username = request.POST['username']
        email_id = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        # password match condition
        if password == password2:
            if User.objects.filter(email=email_id).exists():
                # If email already exists then redirect to same sign-up page
                messages.info(request, 'This Email is alredy taken.')
                return redirect('signup')

            # elif User.objects.filter(username=username).exists():
            #     # If Username already exists then redirect to same sign-up page
            #     messages.info('This Username is alredy taken. Please user some other username')
            #     return redirect('signup')

            else:
                # If email and username don't exists then create a new user
                # Here I am taking email_id as username 
                user = User.objects.create_user(username=email_id, email=email_id, password=password)
                user.first_name = firstname
                user.last_name = lastname

                # by default we are making it "Inactive", User will have to activate by clicking on activation link from their mail
                user.is_active = False 
                user.save()

                current_site = get_current_site # getting the current url of the page
                email_subject = "Activate Your Account"
                message = render_to_string('account/activate.html', {
                    'user': user,
                    'domain': '127.0.0.1:8000',
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)), # converting user id into bytes and encoding it
                    'token': genrate_token.make_token(user)
                })

                #send a message
                email_message = EmailMessage(email_subject, "pintu@logicrays.com", [email_id])
                EmailThread(email_message).start()
                messages.info(request, "Activate Your Account by clicking on activation link in your email")
                messages.success(request, 'Account successfully created for ' + user.first_name)

                # Once the user is created and activated account using activation link
                # then log the user in and redirect to home page
                user_login = authenticate(username=email_id, password=password)
                # login(request, user_login)
                print('user_longin===>', user_login)

                # Creating a customer object for a new user
                user_model = User.objects.get(username=email_id)
                print(user_model)

                new_customer = Customer.objects.create(user=user_model, id_user=user_model.id, email=user_model.email, firstname=user_model.first_name, lastname=user_model.last_name)
                new_customer.save()
                return redirect('index-page')
        else:
            messages.info(request, "Password didn't match. Please enter the same password again")
            return redirect('signup')


    return render(request, 'account/signup.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')
    elif request.method == "POST":
        email_id = request.POST['email']
        password = request.POST['password']

        # check if user already exists or not using email_id
        check_if_user_exists = User.objects.filter(username=email_id).exists()

        # If user exists on this email_id
        if check_if_user_exists:           
            user = authenticate(request, username=email_id, password=password)

            if user is not None:
                # This user is authenticated and valid
                login(request, user)
                messages.success(request, "Login successful")
                return redirect('/')
            else: 
                # Email_id is valid but password didn't match
                messages.warning(request, "Wrong passwrod. Please try again")
                return redirect('login')
        else:
            # user doesn't exists on this email_id
            messages.info(request, "Email Id not found. Please check your email id")
            return redirect('login')

    return render(request, 'account/login.html')

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.info(request, "You are logged out")
    return redirect('/')

class ActivateAccountView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64)) # whatever it gets, will be converted into text format
            user = User.objects.get(pk=uid)
            print('user--->', user)
            print('user type--->', type(user))
        except Exception as indetifier:
            print('No user found')
            user = None
        
        if user is not None and genrate_token.check_token(user, token):
            user.is_active = True
            user.save()
            messages.info(request, "Account activate successfully")
            return redirect("login")
        return render(request, 'account/activatefail.html')