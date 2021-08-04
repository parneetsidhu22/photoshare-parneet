from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login,logout
from .models import Profile
from django.contrib.auth.decorators import login_required
import json

from .models import Post,Profile
from home.models import Friend,Likes,Comment

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
    
    profile = Profile.objects.all().filter(username=request.user.username)[0]
    if request.method == "POST":
        process_type = request.POST.get('process_type')

        if process_type == "profile":
            
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')     
            try:
                profile_image = request.FILES.get('profile_image')
                if profile_image:
                    
                    profile.image = profile_image
                    profile.save()
            except:
                pass

            cur_user = User.objects.all().filter(username=request.user.username)[0]
            cur_user.first_name = first_name
            cur_user.last_name = last_name
            cur_user.email = email
            cur_user.save()

        elif process_type == "change_password":
            old_password = request.POST.get('old_password')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            user = authenticate(username=request.user.username,password=old_password)
            if user is not None:
                
                if password != confirm_password:
                    return HttpResponse(json.dumps({"status":400,"error_tag":"password","error":"Password does not match!"}), content_type="application/json")
                elif len(password) < 8:
                    return HttpResponse(json.dumps({"status":400,"error_tag":"password","error":"Password must be at least 8 characters long!"}), content_type="application/json")
                elif password == old_password:
                    return HttpResponse(json.dumps({"status":400,"error_tag":"password","error":"New password must be different!"}), content_type="application/json")

                user.set_password(password)
                user.save()

                return HttpResponse(json.dumps({"status":200}), content_type="application/json") 
            else:
                return HttpResponse(json.dumps({"status":400,"error_tag":"old_password","error":"Wrong password!"}), content_type="application/json") 
        elif process_type == "private":
            if profile.private:
                profile.private = False
            else:
                profile.private = True
            
            profile.save()
            return HttpResponse(json.dumps({"status":200}), content_type="application/json")

        elif process_type == "disable":
            if profile.disabled:
                profile.disabled = False
            else:
                profile.disabled = True
            
            profile.save()
            return HttpResponse(json.dumps({"status":200}), content_type="application/json") 

        elif process_type == "delete_account":
            password = request.POST.get('password')
            user = authenticate(username=request.user.username,password=password)
            if user is not None:
                posts = Post.objects.all().filter(username = request.user.username)
                profile = Profile.objects.all().filter(username = request.user.username)[0]
                profile.delete()

                comments = Comment.objects.all().filter(username=request.user.username)
                for comment in comments:
                    comment.delete()
                
                f1 = Friend.objects.all().filter(followed=request.user.username)
                for f in f1:
                    f.delete()

                f2 = Friend.objects.all().filter(follower=request.user.username)
                for f in f2:
                    f.delete()

                likes = Likes.objects.all().filter(username=request.user.username)
                for like in likes:
                    like.delete()

                for post in posts:
                    post.delete()
                
                user.delete()

            else:
                return HttpResponse(json.dumps({"status":400}), content_type="application/json") 

            return HttpResponse(json.dumps({"status":200}), content_type="application/json") 

    profile = Profile.objects.all().filter(username=request.user.username)[0]

    context = {
        'profile_image':profile.image.url,
        'disabled':profile.disabled,
        'private':profile.private,
        #extras
        'page_type':'settings'
    }
    
    return render(request,'user_authentication/settings.html',context=context)