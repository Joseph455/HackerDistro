from django.contrib import admin
from .models import (
    UserModel,
    StoryModel,
    JobModel,
    CommentModel,
    PollModel,
    PollOptionModel
)
# Register your models here.

admin.site.register(UserModel)
admin.site.register(StoryModel)
admin.site.register(JobModel)
admin.site.register(CommentModel)
admin.site.register(PollModel)
admin.site.register(PollOptionModel)

