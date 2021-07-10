from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from user_authentication.models import Profile,Post
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Friend,Likes
import json

@login_required(login_url='/user_authentication/login')
def homepage(request):

    if request.method == "POST":
        image = request.FILES['image']
        if image is not None:
            post = Post(
                username=request.user.username,
                image=image
            )
            post.save()

    profile = Profile(username=request.user.username)
    name = request.user.first_name + ' ' + request.user.last_name


    if len(name) > 17:
        name = request.user.first_name

    # getting all posts
    posts = Post.objects.all().filter(username=request.user.username).order_by('-pk')
    total_posts = len(posts)
    if total_posts >= 1000:
        total_posts = total_posts/1000
        total_posts = str(total_posts)[:4] + "k"
    

    # checking for friend requests
    total_requests = len(Friend.objects.filter(followed=request.user.username,status=False))

    #getting followers and following
    total_followers = len(Friend.objects.filter(followed=request.user.username,status=True))
    if total_followers >= 1000:
        total_followers = total_followers/1000
        total_followers = str(total_followers)[:4] + "k"
    
    total_followings = len(Friend.objects.filter(follower=request.user.username,status=True))
    if total_followings >= 1000:
        total_followings = total_followings/1000
        total_followings = str(total_followings)[:4] + "k"


    context = {
        'img':profile.image,
        'username':request.user.username,
        'name': name,
        'posts':posts,
        'total_posts':total_posts,
        'total_requests':total_requests,
        'total_followings':total_followings,
        'total_followers':total_followers
    }
    
    return render(request,'home/index.html',context=context)

@login_required(login_url='/user_authentication/login')
def add_friend(request):
    results = []

    if request.method == 'POST':
        method = request.POST.get('method')
        followed = request.POST.get('followed')
        friend = Friend(follower=request.user.username,followed=followed)
        friend.save()


    profiles = []
    results = User.objects.all().filter(
        Q(first_name__icontains=request.GET.get('q').split()[0]) | Q(last_name__icontains=request.GET.get('q')) | Q(username=request.GET.get('q'))
        ).distinct()
    res = []
    followed = []

    try:
        for result in results:
            if result.username != request.user.username:
                friend = Friend.objects.filter(Q(followed=result.username,follower=request.user.username)|Q(followed=request.user.username,follower=result.username))
                profile = Profile(username=result.username)
                if len(friend) == 0:
                    res.append(result)
                    profiles.append(profile)
                else:
                    followed.append((result,profile))
    except:
        return redirect('homepage')
                



    data = zip(res,profiles)

    return render(request,'home/add_friend.html',context={"information":data,'q':request.GET.get('q'),"followed":followed})

@login_required(login_url='/user_authentication/login')
def friend_request_list(request):

    if request.method == 'POST':
        meth = request.POST.get('method')
        follower = request.POST.get('follower')
        print(meth)
        if meth == 'accept':
            try:
                friend = Friend.objects.get(follower=follower,followed=request.user.username)
                friend.status = True
                friend.save()
            except:
                pass
        elif meth == 'unfollow':
            
            friend = Friend.objects.all().get(Q(follower=request.user.username,followed=follower) |
                                                Q(follower=follower,followed=request.user.username))
            print(friend)
            friend.delete()
            

        elif meth == 'reject':
            try:
                friend = Friend.objects.get(follower=follower,followed=request.user.username)
                friend.delete()
            except:
                pass

    requests = Friend.objects.filter(followed=request.user.username,status=False)
    profiles = []
    data = []
    for req in requests:
        profile = Profile(username=req.follower)
        profiles.append(profile)

        data.append(User.objects.all().filter(username=req.follower)[0])

    requests = zip(data,profiles)
    return render(request,'home/friend_request_list.html',context={"requests":requests})

@login_required(login_url='/user_authentication/login')
def post_data(request):
    if request.method != "POST":
        return redirect('homepage')
    posts = Post.objects.all().filter(username=request.user.username).order_by('-pk')

    followers = Friend.objects.all().filter(followed=request.user.username,status=True)
    for foll in followers:
        foll_posts = Post.objects.all().filter(username=foll.follower)
        posts = posts | foll_posts

    following = Friend.objects.all().filter(follower=request.user.username,status=True)
    for foll in following:
        foll_posts = Post.objects.all().filter(username=foll.followed)
        posts = posts | foll_posts

    posts = posts.order_by('-pk')

    responseData = []


    for post in posts:
        user = User.objects.all().filter(username=post.username)[0]

        if user is not None:
            profile = Profile.objects.all().filter(username=post.username)[0]
            like = Likes.objects.all().filter(username=request.user.username,postid=post.pk)
            if len(like) != 0:
                liked = "fa fa-heart"
            else:
                liked = "fa fa-heart-o"   
            
            responseData.append({
                "post_id":post.pk,
                "username":post.username,
                "name":user.first_name + " " + user.last_name,
                "image":post.image.url,
                "likes":post.likes,
                "profile_img":profile.image.url,
                "liked": liked
            })

    return HttpResponse(json.dumps(responseData), content_type="application/json") 

@login_required(login_url='/user_authentication/login')
def like_post(request):
    if request.method == "POST":
        postid = request.POST.get('post_id')

        like = Likes.objects.all().filter(username=request.user.username,postid=postid)
        print(len(like))

        post = Post.objects.all().filter(pk=postid)[0]

        
        if len(like) == 0:
            post.likes = post.likes + 1
            post.save()
            newlike = Likes(username=request.user.username,postid=postid)
            newlike.save()
        else:
            post.likes = post.likes  - 1
            post.save()
            like.delete()

        print(postid)

    return redirect('homepage')