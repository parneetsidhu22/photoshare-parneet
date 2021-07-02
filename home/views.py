from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from user_authentication.models import Profile


@login_required(login_url='/user_authentication/login')
def homepage(request):
    profile = Profile(username=request.user.username)
    name = request.user.first_name + ' ' + request.user.last_name
    if len(name) > 17:
        name = request.user.first_name
    context = {
        'img':profile.image,
        'username':request.user.username,
        'name': name
    }
    return render(request,'home/index.html',context=context)
