from django.contrib.auth.models import User, auth
from .models import Profile, Post, LikePost, FollowersCount
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.


@login_required(login_url='login')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    posts = Post.objects.all()
    return render(request, 'index.html',{'user_profile':user_profile, 'posts':posts})


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password2']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email is already registered')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username is already registered')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username, email=email, password=password)
                user.save()

                user_login = auth.authenticate(
                    username=username, password=password)
                auth.login(request, user_login)

                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password not matching')
            return redirect('signup')
    else:
        return render(request, 'signup.html')


def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid credentials')
            return redirect('login')
    else:
        return render(request, 'signin.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')


@login_required(login_url='login')
def settings(request):
    user_profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        if request.FILES.get('image') == None:
            user_profile.profile_img = request.POST['image']
            user_profile.bio = request.POST['bio']
            user_profile.locations = request.POST['location']
            user_profile.save()
        else:
            user_profile.profile_img = request.FILES.get('image')
            user_profile.bio = request.POST['bio']
            user_profile.locations = request.POST['location']
            user_profile.save()
        return redirect('settings')
    return render(request, 'settings.html', {'user_profile': user_profile})

@login_required(login_url='login')
def upload(request):
    if request.method=="POST":
        user=request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user=user, image=image , caption=caption)
        new_post.save()
        return redirect('/')

    else:
        return redirect('/')

@login_required(login_url='login')
def like_post(request):
    username = request.user.username
    post_id = request.GET.get('post_id')
    print(post_id)
    posts=Post.objects.get(id=post_id)

    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        posts.no_of_likes += 1
        posts.save()
        return redirect ('/')
    else:
        print(111111111111)
        like_filter.delete()
        posts.no_of_likes -= 1
        posts.save()

        return redirect ('/')

@login_required(login_url='login')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    user_profile = Profile.objects.get(user=user_object)
    user_posts = Post.objects.filter(user=pk)
    user_post_length = len(user_posts)
    follower = request.user.username
    user = pk
    if FollowersCount.objects.filter(follower=follower, user=user).first():
        button_text = 'Unfollow'
    else:
        button_text='Follow'

    user_followers = len(FollowersCount.objects.filter(user=pk))
    user_following = len(FollowersCount.objects.filter(follower=pk))
    context = {
        'user_object':user_object, 
        'user_profile': user_profile,
        'user_posts':user_posts,
        'user_post_length':user_post_length,
        'button_text':button_text,
        'user_followers':user_followers,
        'user_following':user_following,
        }
    return render(request,'profile.html',context)

@login_required(login_url='login')
def follow(request):
    if request.method=="POST":
        follower = request.POST['follower']
        user = request.POST['user']
        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user+'/')

        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user+'/')
    else:
        return redirect('/')