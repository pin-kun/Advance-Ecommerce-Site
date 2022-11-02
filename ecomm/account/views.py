from email import message
from tabnanny import check
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Customer 

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
                myuser = User.objects.create_user(username=email_id, email=email_id, password=password)
                myuser.first_name = firstname
                myuser.last_name = lastname
                myuser.save()
                print(myuser)
                messages.success(request, 'Account created for ' + myuser.first_name)

                # Once the user is created then log user in and redirect to home page
                user_login = authenticate(username=email_id, password=password)
                login(request, user_login)

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
            myuser = authenticate(request, username=email_id, password=password)

            if myuser is not None:
                # This user is authenticated and valid
                login(request, myuser)
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

def logout_view(request):
    logout(request)
    messages.info(request, "You are logged out")
    return redirect('/')