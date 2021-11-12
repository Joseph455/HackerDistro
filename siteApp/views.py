
import asyncio
from siteApp.forms import CommentForm, JobForm, PollForm, PollOptionForm, StoryForm

from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.http.response import HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods
from django.urls import reverse

from .models import BaseModel, CommentModel, PollOptionModel
from .search import comment_search, full_search



@require_http_methods(["GET"])
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

@require_http_methods(["GET"])
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

@require_http_methods(["GET"])
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


@require_http_methods(["POST"])
def create_story_view(request, *args, **kwargs):
    form =  StoryForm(request.POST)
    if form.is_valid():
        story = form.pre_save()
        story.save()
        return redirect(reverse("site-app:list-items"))
    else:
        messages.error(request, form.errors)
        return reverse("site-app:list-items")

@require_http_methods(["POST"])
def create_job_view(request, *args, **kwargs):
    form =  JobForm(request.POST)
    if form.is_valid():
        job = form.pre_save()
        job.save()
        return redirect(reverse("site-app:list-items"))
    else:
        messages.error(request, form.errors)
        return redirect(reverse("site-app:list-items"))

@require_http_methods(["POST"])
def create_poll_view(request, *args, **kwargs):
    form =  PollForm(request.POST)
    if form.is_valid():
        poll = form.pre_save()
        poll.save()
        return redirect(reverse("site-app:list-items"))
    else:
        messages.error(request, form.errors)
        return redirect(reverse("site-app:list-items"))

@require_http_methods(["POST"])
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
    else:
        messages.error(request, form.errors)
        return redirect(reverse("site-app:retreive_items", kwargs={"id": item_id}))

@require_http_methods(["POST"])
def create_polloption_view(request, poll_id, *args, **kwargs):
    form =  PollOptionForm(request.POST)
    if form.is_valid():
        poll = form.pre_save()
        parent = get_object_or_404(BaseModel, id=poll_id)
        poll.parent = parent.get_model_type()
        poll.save()
        return redirect(reverse("site-app:retreive_items", kwargs={"id": poll_id}))
    else:
        messages.error(request, form.errors)
        return redirect(reverse("site-app:retreive_items", kwargs={"id": poll_id}))


