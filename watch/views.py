from multiprocessing import context
from django.shortcuts import render,redirect
from django.http  import HttpResponse, Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from .forms import UserRegisterForm,UserLoginForm
from .models import Profile, Neighbourhood, healthservices, Business, Health, Authorities, BlogPost, notifications, Comment
from .forms import notificationsForm, ProfileForm, BlogPostForm, BusinessForm, CommentForm
import json
from django.contrib.auth import (
    authenticate,
    get_user_model,
    login,
    logout
)
import datetime as dt
from django.db.models import Q
from django.contrib.auth.models import User

# Create your views here.
def index(request):
  try:
    if not request.user.is_authenticated:
      return redirect('/accounts/login/')
    current_user = request.user
    profile = Profile.objects.all()
  except ObjectDoesNotExist:
    return redirect('create-profile')

  return render(request, 'index.html')

@login_required(login_url='/accounts/login/')
def notification(request):
  current_user = request.user
  profile = Profile.objects.all()
  all_notifications = notifications.objects.all()

  return render(request, 'notifications.html', {"notifications":all_notifications})

@login_required(login_url='/accounts/login/')
def blog(request):
  current_user=request.user
  profile = Profile.objects.all()
  blogposts = BlogPost.objects.all()

  return render(request, 'blog.html', {"blogposts":blogposts})

@login_required(login_url='/accounts/login/')
def health(request):
  current_user = request.user
  profile = Profile.objects.all()
  healthservices = Health.objects.all()

  return render(request, 'health.html', {"healthservices":healthservices})

@login_required(login_url='/accounts/login/')
def authorities(request):
  current_user=request.user
  profile=Profile.objects.all()
  authorities=Authorities.objects.all()

  return render(request, 'authorities.html', {"authorities":authorities})

@login_required(login_url='/accounts/login/')
def businesses(request):
  current_user = request.user
  profile = Profile.objects.all()
  businesses = Business.objects.all()

  return render(request, 'business.html', {"businesses":businesses})

@login_required(login_url='/accounts/login/')
def view_blog(request, id):
  
  try:
    comments = Comment.objects.filter(post_id=id)
  except:
    comments = []

  blog = BlogPost.objects.get(id=id)
  if request.method == 'POST':
    form = CommentForm(request.POST, request.FILES)
    if form.is_valid():
      comment = form.save(commit=False)
      comment.username = request.user
      comment.post = blog
      comment.save()
  else:
    form = CommentForm()
    return render(request, 'view_blog.html', {"blog":blog, "form":form, "comments":comments})

@login_required(login_url='/accounts/login/')
def my_profile(request):
  current_user = request.user
  profile = Profile.objects.all()

  return render(request, 'user_profile.html', {"profile":profile})

@login_required(login_url='/accounts/login/')
def user_profile(request, username):
  user = User.objects.get(username = username)
  profile = Profile.objects.get(username = user)

  return render(request, 'user_profile.html', {"profile":profile})

@login_required(login_url='/accounts/login/')
def create_profile(request):
  current_user=request.user
  if request.method == "POST":
    form = ProfileForm(request.POST, request.FILES)
    if form.is_valid():
      profile = form.save(commit=False)
      profile.username = current_user
      profile.save()
    return HttpResponseRedirect('/')

  else:
    form = ProfileForm()
  return render(request, 'profile_form.html', {"form":form})

@login_required(login_url='/accounts/login/')
def update_profile(request):
  current_user = request.user
  if request.method == "POST":
    instance = Profile.objects.all()
    form = ProfileForm(request.POST, request.FILES)
    if form.is_valid():
      profile = form.save(commit = False)
      profile.username = current_user
      profile.save()

    return redirect('index')

  elif Profile.objects.all():
    profile = Profile.objects.all()
    form = ProfileForm(instance=profile)
  else:
    form = ProfileForm()

  return render(request, 'update_profile.html', {"form":form})

@login_required(login_url='/accounts/login/')
def new_blogpost(request):
  current_user = request.user
  profile = Profile.objects.all()

  if request.method == 'POST':
    form  = BlogPostForm(request.POST, request.FILES)
    if form.is_valid():
      blogpost = form.save(commit = False)
      blogpost.username = current_user
      blogpost.neighbourhood = profile.neighbourhood
      blogpost.save()

    return HttpResponseRedirect('/blog')

  else:
    form = BlogPostForm()

  return render(request, 'blogpost_form.html', {"form":form})

@login_required(login_url='/accounts/login/')
def new_business(request):
  current_user = request.user
  profile = Profile.objects.get(username=current_user)

  if request.method == "POST":
    form = BusinessForm(request.POST, request.FILES)
    if form.is_valid():
      business = form.save(commit=False)
      business.owner = current_user
      business.neighbourhood = profile.neighbourhood
      business.save()

    return HttpResponseRedirect('/businesses')

  else:
    form = BusinessForm()

  return render(request, 'business_form.html', {"form":form})

@login_required(login_url='/accounts/login/')
def new_notification(request):
  current_user = request.user
  profile = Profile.objects.all()

  if request.method == "POST":
    form = notificationsForm(request.POST, request.FILES)
    if form.is_valid():
      notification = form.save(commit=False)
      notification.author = current_user
      notification.neighbourhood = profile.neighbourhood
      notification.save()

      if notification.priority == 'High Priority':
        # send_priority_email(profile.name, profile.email, notification.title, notification.notification, notification.author, notification.neighbourhood)

       return HttpResponseRedirect('/notifications')

  else:
    form = notificationsForm()

  return render(request, 'notifications_form.html', {"form":form})

@login_required(login_url='/accounts/login/')
def search_results(request):
  if 'blog' in request.GET and request.GET["blog"]:
    search_term = request.GET.get("blog")
    searched_blogposts = BlogPost.search_blogpost(search_term)
    message = f"{search_term}"

    print(searched_blogposts)

    return render(request, 'search.html', {"message":message, "blogs":searched_blogposts})

  else:
    message = "You haven't searched for any term"
    return render(request, 'search.html', {"message":message})


def register_view(request):
    next = request.GET.get('next')
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        new_user = authenticate(username=user.username, password=password)
        login(request, new_user)
        if next:
            return redirect(next)
        return redirect('login')
    context = {
        'form': form,
    }
    return render(request, "registration/registration_form.html", context)

    

def login_view(request):
    next = request.GET.get('next')
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)
        login(request, user)
        
        if next:
            return redirect(next)
        return redirect('index')

    context = {
        'form': form,
    }
    return render(request, "registration/login.html", context)