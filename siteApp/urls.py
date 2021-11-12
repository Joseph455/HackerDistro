from django.urls.conf import path, re_path

from .views import (
    list_view, 
    retreive_view, 
    comment_view,
    create_comment_view,
    create_job_view,
    create_poll_view,
    create_story_view,
    create_polloption_view,
)

app_name="site-app"

urlpatterns = [
    path("items/", list_view, name="list-items"),
    path("items/<int:id>/", retreive_view, name="retreive_items"),
    path("comments/<int:id>/", comment_view, name="comment_detail"),
    path("items/jobs/", create_job_view, name="create_job"),
    path("items/stories/", create_story_view, name="create_story"),
    path("items/polls/", create_poll_view, name="create_poll"),
    path("items/polls/<int:poll_id>/options/", create_polloption_view, name="create_pollopt"),
    path("items/<int:item_id>/comments/", create_comment_view, name="create-comment"),
]


