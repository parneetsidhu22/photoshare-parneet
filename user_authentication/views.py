from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login,logout
from .models import Profile
from django.contrib.auth.decorators import login_required

def loginpage(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    context = {}
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)
        
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request,"Wrong username or password!",extra_tags="authentication_error")
            context = {"errors" : True,"username":username}
    
    return render(request,'user_authentication/login.html',context=context)

def registerpage(request):
    if request.user.is_authenticated:
        return redirect('homepage')

    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cpassword = request.POST.get('cpassword')

        error = False
        username_error = False
        password_error = False

        if not username.isalnum():
            error = True
            messages.error(request,"Username must be alphanumeric!",extra_tags='username_error')
            username_error = True

        usercheck = User.objects.filter(username=username)
        print(usercheck)
        if usercheck.exists():
            error = True
            messages.error(request,"Username already exists!",extra_tags='username_error')
            username_error = True

        if password != cpassword:
            error = True
            messages.error(request,"Password does not match!",extra_tags="password_error")
            password_error = True
        if len(list(password)) < 8:
            error = True
            messages.error(request,"Password must be at least 8 characters long!",extra_tags="password_error")
            password_error = True

        if error:
            print('errors')
            context={
                "first_name":first_name,
                "last_name":last_name,
                "username":username,
                "email":email,
                "username_error":username_error,
                "password_error":password_error
            }
            print(context)
            return render(request,'user_authentication/register.html',context=context)
        else:
            user = User(username=username,email=email)
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            user = authenticate(username=username,password=password)
            profile = Profile(username=username)
            profile.save()

            if user is not None:
                login(request, user)
                return redirect('homepage')  


    return render(request,'user_authentication/register.html')


def logoutpage(request):
    if not request.user.is_authenticated:
        return redirect('loginpage')
    logout(request)
    return redirect("loginpage")


@login_required(login_url='/user_authentication/login')
def settingspage(request):
    profile = Profile(username=request.user.username)
    name = request.user.first_name + ' ' + request.user.last_name

    context = {
        'img':profile.image,
        'username':request.user.username,
        'name': name,
        'email': request.user.email
    }
    
    return render(request,'user_authentication\settings.html',context=context)