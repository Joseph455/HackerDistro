
import asyncio

from django.contrib.auth import authenticate, login, logout

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods, require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .forms import (
    CommentForm, 
    JobForm, 
    PollForm, 
    PollOptionForm, 
    StoryForm, 
    UserLoginForm, 
    UserSubscriptionForm,
    ResetPasswordForm
)

from .models import BaseModel, CommentModel, UserModel, PollOptionModel
from .search import comment_search, full_search


@require_GET
def list_view(request, *args, **kwargs):
    filters = [
        'job',
        'story',
        'poll'
    ]

    filter = request.GET.get('filter', None)
    query =  request.GET.get('search', None)

    if query:
        query_set = full_search(query)
    else:

        if filter and filter in filters:
            query_set = BaseModel.objects.all(
            ).exclude(type="comment").exclude(type="pollopt").order_by("time").reverse().filter(type=filter)
        else:
            query_set = BaseModel.objects.all(
            ).exclude(type="comment").exclude(type="pollopt").order_by("time").reverse()

    query_set = [q.get_model_type() for q in query_set]
    paginator = Paginator(query_set, 6)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(
        request, 
        "list.html", 
        {
            "page_obj": page_obj, 
            "filters": filters, 
            "page_filter": filter,
            "story_form": StoryForm,
            "poll_form": PollForm,
            "job_form": JobForm,
        }
    )


@require_GET
def retreive_view(request, id:int, *args, **kwargs):
    base_obj = get_object_or_404(BaseModel, id=id)
    obj = base_obj.get_model_type()
    query =  request.GET.get('search', None)

    if query:
        comments = comment_search(query, id)
    else:
        comments = CommentModel.objects.filter(parent__id=obj.id)

    paginator = Paginator(comments, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request, 
        "detail.html", 
        {
            'page_obj': page_obj,
            "obj": obj,
            "pollopt_form": PollOptionForm,
            "comment_form": CommentForm,
        },        
    )


@require_GET
def comment_view(request, id:int, *args, **kwargs):
    comment = get_object_or_404(CommentModel, id=id)
    
    query =  request.GET.get('search', None)
    
    if comment.kids:
        try:
            asyncio.run(comment.load_kids())
        except Exception as e:
            print(e)

    replies =  CommentModel.objects.filter(parent__id=comment.id)
    
    if query:
        replies = comment_search(query, id)

    paginator = Paginator(replies, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request, 
        "detail.html", 
        {
            'page_obj': page_obj,
            "obj": comment,
            "comment_form": CommentForm,
        }
    )


@require_POST
@login_required
def create_story_view(request, *args, **kwargs):
    form =  StoryForm(request.POST)

    if form.is_valid():
        story = form.pre_save()
        story.save()
        return redirect(reverse("site-app:list-items"))

    messages.error(request, form.errors)
    return reverse("site-app:list-items")


@require_POST
@login_required
def create_job_view(request, *args, **kwargs):
    form =  JobForm(request.POST)

    if form.is_valid():
        job = form.pre_save()
        job.save()
        return redirect(reverse("site-app:list-items"))

    messages.error(request, form.errors)
    return redirect(reverse("site-app:list-items"))


@require_POST
@login_required
def create_poll_view(request, *args, **kwargs):
    form =  PollForm(request.POST)

    if form.is_valid():
        poll = form.pre_save()
        poll.save()
        return redirect(reverse("site-app:list-items"))

    messages.error(request, form.errors)
    return redirect(reverse("site-app:list-items"))


@require_POST
@login_required
def create_comment_view(request, item_id, *args, **kwargs):
    form =  CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.pre_save()
        parent = get_object_or_404(BaseModel, id=item_id)
        comment.parent = parent.get_model_type()

        if comment.parent.type in ["story", "poll"]:
            comment.parent.descendants += 1
            comment.parent.save()
    
        comment.save()
        return redirect(reverse("site-app:retreive_items", kwargs={"id": item_id}))

    messages.error(request, form.errors)
    return redirect(reverse("site-app:retreive_items", kwargs={"id": item_id}))


@require_POST
@login_required
def create_polloption_view(request, poll_id, *args, **kwargs):
    form =  PollOptionForm(request.POST)

    if form.is_valid():
        poll = form.pre_save()
        parent = get_object_or_404(BaseModel, id=poll_id)
        poll.parent = parent.get_model_type()
        poll.save()
        return redirect(reverse("site-app:retreive_items", kwargs={"id": poll_id}))

    messages.error(request, form.errors)
    return redirect(reverse("site-app:retreive_items", kwargs={"id": poll_id}))


@require_POST
def user_login(request, *args, **kwargs):
    form = UserLoginForm(request.POST)

    next = request.query.get(
        'next', 
        reverse("site-app:list_view")
    )

    if form.is_valid():
        
        data = {
            "email" : form.cleaned_data.get("email"),
            "password" : form.cleaned_data.get("password")
        }

        user = authenticate(request=request, **data)

        if user:
            login(request, user)
            return redirect(next)

        message = "Invalid email or Password"
        messages.error(request, message)
        return redirect(next)

    messages.error(request, form.errors)
    return redirect(next)


@require_POST
def user_subscription(request, *args, **kwargs):
    form = UserSubscriptionForm(request.POST)
    
    next = request.query.get(
        'next', 
        reverse("site-app:list_view")
    )

    if form.is_valid():
        user = form.save()
        user.set_password(form.cleaned_data.get("password"))
        user.save()

        hacker = UserModel.objects.create(user=user)
        hacker.site_created = True
        hacker.save()
        login(request, user)
        return redirect(next)

    messages.error(request, form.errors)
    return redirect(next)


@require_POST
@login_required
def user_logout(request, *args, **kwargs):
    
    next = request.query.get(
        'next', 
        reverse("site-app:list_view")
    )

    logout(request)
    return redirect(next)


@require_POST
@login_required
def reset_password(request, *args, **kwargs):
    form = ResetPasswordForm(request.POST)
    user = request.user

    if form.is_valid(request):
        pwd = form.cleaned_data.get('new_password')
        user.set_password(pwd)
        user.save()
        logout(request)
        login(request, user)

        return redirect(
            reverse('site-app:profile_view', {"id": user.id})
        )
    
    messages.error(request, form.errors)
    
    return redirect(reverse('site-app:profile_view', {"id": user.id}))


@require_GET
def user_profile(request, id, **kwargs):
    user = User.objects.get(id=id)
    hacker = UserModel.objects.get(user=user)
    return render(request, "profile.html", {
        'user': user,
        'hacker': hacker,
    })
