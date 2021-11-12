from django.db.models import Q
from siteApp.models import CommentModel, JobModel, PollModel, StoryModel


def comment_search(text, id):
    result = list(
        CommentModel.objects.all().filter(
            Q(parent__id=id)&
            (Q(text__icontains=text)|
            Q(by__source_id__icontains=text))
        )
    )
    return result


def full_search(text):
    jobs = JobModel.objects.all().filter(
        Q(title__icontains=text)|
        Q(text__icontains=text)|
        Q(by__source_id__icontains=text)
    )
    
    polls = PollModel.objects.all().filter(
        Q(title__icontains=text)|
        Q(text__icontains=text)|
        Q(by__source_id__icontains=text)
    )

    stories = StoryModel.objects.all().filter(
        Q(title__icontains=text)|
        Q(by__source_id__icontains=text)
    )

    result = list(jobs)+list(polls)+list(stories)
    return result
