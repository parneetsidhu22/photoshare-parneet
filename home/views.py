from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from user_authentication.models import Profile,Post
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Friend,Likes,Comment
import json
from datetime import datetime
from django.contrib.humanize.templatetags import humanize

@login_required(login_url='/user_authentication/login')
def homepage(request):
    if Profile.objects.all().filter(username=request.user.username)[0].disabled:
        return render(request,'home/disable.html',context={"me":True})

    if request.method == "POST":
        image = request.FILES['image']
        description = request.POST.get('description')
        if image is not None:
            post = Post(
                username=request.user.username,
                image=image,
                description = description
            )
            post.save()

    profile = Profile.objects.all().filter(username=request.user.username)[0]
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
        'img':profile.image.url,
        'username':request.user.username,
        'name': name,
        'posts':posts,
        'total_posts':total_posts,
        'total_requests':total_requests,
        'total_followings':total_followings,
        'total_followers':total_followers,
        #extras
        'page_type':'home'
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
    q = request.GET.get('q')
    first_name = ''
    last_name = ''

    try:
        typ = request.GET.get('type')
        first_name = request.GET.get('q').split()[0]
        last_name = request.GET.get('q').split()[1]
    except:
        pass

    if last_name == '':
        last_name = first_name

    if typ is None:
        results = User.objects.all().filter(
            Q(first_name__icontains=first_name) | Q(last_name__icontains=last_name) | Q(username=request.GET.get('q'))
            ).distinct()
    elif typ == 'followers':
        followers = Friend.objects.all().filter(followed=request.user.username)
        for follower in followers:
            results.append(User.objects.all().filter(username=follower.follower)[0])
    elif typ == 'following':
        print('hi')
        followings = Friend.objects.all().filter(follower=request.user.username)
        for following in followings:
            results.append(User.objects.all().filter(username=following.followed)[0])
    res = []
    followed = []

    try:
        for result in results:
            if not Profile.objects.all().filter(username=result.username)[0].disabled:
                if result.username != request.user.username:
                    friend = Friend.objects.filter(Q(followed=result.username,follower=request.user.username)|Q(followed=request.user.username,follower=result.username))
                    profile = Profile.objects.all().filter(username=result.username)[0]
                    if len(friend) == 0:
                        res.append(result)
                        profiles.append(profile)
                    else:
                        followed.append((result,profile))
    except:
        return redirect('homepage')
                



    data = zip(res,profiles)

    q = request.GET.get('q')
    if q is None: q = ''

    return render(request,'home/add_friend.html',context={"information":data,'q':q,"followed":followed})

@login_required(login_url='/user_authentication/login')
def friend_request_list(request):

    if request.method == 'POST':
        meth = request.POST.get('method')
        follower = request.POST.get('follower')
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

    requests = []
    for i in range(len(data) - 1,-1,-1):
        requests.append([data[i],profiles[i]])
    #requests = zip(data,profiles)
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
        if not Profile.objects.all().filter(username=post.username)[0].disabled:
            
            user = User.objects.all().filter(username=post.username)[0]

            if user is not None:
                
                profile = Profile.objects.all().filter(username=post.username)[0]
                like = Likes.objects.all().filter(username=request.user.username,postid=post.pk)
                total_comments = 0
                comments = Comment.objects.all().filter(postid=post.pk)
                for comment in comments:
                    p = Profile.objects.all().filter(username=comment.username)[0]
                    if not p.disabled:
                        total_comments += 1

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
                    "liked": liked,
                    "total_comments":total_comments,
                    "commentDisable":post.commentDisable,
                    "description":post.description
                })
    return HttpResponse(json.dumps(responseData), content_type="application/json") 

@login_required(login_url='/user_authentication/login')
def like_post(request):
    if request.method == "POST":
        postid = request.POST.get('post_id')

        like = Likes.objects.all().filter(username=request.user.username,postid=postid)

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


    return redirect('homepage')

@login_required(login_url='/user_authentication/login')
def add_comment(request):
    if request.method == "POST":
        comment = request.POST.get('comment')
        post_id = request.POST.get('post_id')
        comment = Comment(comment=comment,postid=post_id,username=request.user.username)
        comment.save()
    
    return HttpResponse(json.dumps({"status":200}))

@login_required(login_url='/user_authentication/login')
def get_comments(request):
    if request.method == "POST":
        post_id = request.POST.get('post_id')

        comments = Comment.objects.all().filter(postid=post_id)
        data = []
        for comment in comments[::-1]:

            ago = humanize.naturaltime(comment.time_sent)
            user = User.objects.all().filter(username=comment.username)[0]
            profile = Profile.objects.all().filter(username=comment.username)[0]

            data.append(
                {
                    "first_name":user.first_name,
                    "last_name":user.last_name,
                    "username":comment.username,
                    "post_id":comment.postid,
                    "comment":comment.comment,
                    "ago":ago,
                    "profile_image":profile.image.url,
                    "disabled":profile.disabled
                }
            )

        return HttpResponse(json.dumps(data), content_type="application/json") 


@login_required(login_url='/user_authentication/login')
def operations(request):
    if request.method == "POST":
        operation = request.POST.get('operation')
        pid = request.POST.get('post_id')
        if operation == "delete":
            try:
                post = Post.objects.all().filter(pk=pid)[0]
                comments = Comment.objects.all().filter(postid=pid)
                for comment in comments:
                    comment.delete()
                post.delete()
            except Exception as e:
                return HttpResponse(json.dumps({"status":500}), content_type="application/json") 
        elif operation == "toggle_comment":
            current = request.POST.get('current')
            if current == 'true':
                current = False
            else:
                current = True




            

            post = Post.objects.all().filter(pk = pid)[0]
            post.commentDisable = current
            post.save()


        return HttpResponse(json.dumps({"status":200}), content_type="application/json") 
    return HttpResponse(json.dumps({"status":404}), content_type="application/json") 

@login_required(login_url='/user_authentication/login')
def gallery(request):
    username = request.GET.get('u')

    if not username:
        username = request.user.username

    if Profile.objects.all().filter(username=username)[0].disabled:
        me = (username == request.user.username)

        return render(request,'home/disable.html',context={"me":me})
    
    

    posts = Post.objects.all().filter(username=username)
    images = []
    total_followers = 0
    total_followings = 0
    for post in posts:
        images.append(post.image.url)

    #getting followers and following
    total_followers = len(Friend.objects.filter(followed=username,status=True))
    total_followings = len(Friend.objects.filter(follower=username,status=True))
            
    if total_followers >= 1000:
        total_followers = total_followers/1000
        total_followers = str(total_followers)[:4] + "k"
            
        
    if total_followings >= 1000:
        total_followings = total_followings/1000
        total_followings = str(total_followings)[:4] + "k"

    user = User.objects.all().filter(username=username)[0]
    profile = Profile.objects.all().filter(username=username)[0]
    showPrivate = False
    if profile.private:
        f1 = len(Friend.objects.filter(followed=username,follower=request.user.username))
        f2 = len(Friend.objects.filter(followed=request.user.username,follower=username))
        
        if f1 < 1 and f2 < 1:
            showPrivate = True

    data = {
        "images":images[::-1],
        "posts":len(images),
        "followers":total_followers,
        "followings":total_followings,
        "user":user,
        "profile_img":profile.image.url,
        #extras
        'page_type':'gallery',
        'showPrivate':showPrivate
    }

    return render(request,'home/gallery.html',context=data)

@login_required(login_url='/user_authentication/login')
def get_friends(request):
    if request.method != "POST":
        return redirect('homepage')
    
    username = request.POST.get('username')
    to_show = request.POST.get('to_show')

    if username == None:
        username = request.user.username

    if to_show == 'followers':
        friends = Friend.objects.all().filter(follower=username)
    else:
        friends = Friend.objects.all().filter(followed=username)

    data = []
    for friend in friends:
        if to_show == 'followers':
            u = friend.followers
        else:
            u = friend.following

        profile = Profile.objects.all().filter(username=u)
        user = User.objects.all().filter(username=u)

        data.append({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'image':profile.image.url
        })
    return HttpResponse(json.dumps(data), content_type="application/json") 
