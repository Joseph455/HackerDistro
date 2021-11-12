import asyncio
from typing import Pattern
import aiohttp
import time
from asgiref.sync import sync_to_async

from django.db import models
from django.utils import timezone
from django.conf import settings
from django.urls import reverse


from rest_framework import serializers

from .custom_fields import ListField
# Create your models here.


object_types = (
    ( "job", "job"),
    ("story", "story"),
    ("comment", "comment"),
    ("poll", "poll"),
    ("pollopt", "pollopt"),
)


class BaseModel(models.Model):
    source_id = models.IntegerField(null=True, blank=True, unique=True)
    deleted = models.BooleanField(default=False)
    type = models.CharField(choices=object_types, null=False, max_length=20)
    by = models.ForeignKey("UserModel", on_delete=models.CASCADE)
    time = models.DateTimeField(default=timezone.now)
    dead = models.BooleanField(default=False)
    kids = ListField(null=True, blank=True)
    site_created = models.BooleanField(default=False)

    class Meta:
        ordering = ["time"]

    async def load_kids(self) -> list:
        from .sync import DbSyncTask
        
        if not self.site_created:
            async def task(kid_id) -> models.Model:
                kid_data = await BaseModel.retrieve_data(kid_id)
                if kid_data:
                    kid_obj = await DbSyncTask.process_item(kid_data, False)
                    return kid_obj
        
            tasks = [task(kid_id) for kid_id in (self.kids or [])]

            return await asyncio.gather(*tasks)

    @staticmethod
    async def create(source_id:int) -> tuple:
        try:
            obj =  await sync_to_async(BaseModel.objects.get)(source_id=source_id)
            return (obj, False)
        except BaseModel.DoesNotExist:
            data = await BaseModel.retrieve_data(source_id)

            if data:
                model_list = {
                    "job": JobModel,
                    "story": StoryModel,
                    "comment": CommentModel,
                    "poll": PollModel,
                    "pollopt": PollOptionModel,
                }

                model_class = model_list.get(data.get("type"))
                serializer = model_class.get_Serializer_class()(data=data)
                if serializer.is_valid():
                    return await sync_to_async(model_class.objects.get_or_create)(**await serializer.data)

    @staticmethod
    async def retrieve_data(source_id:int, retries=0) -> dict:
        if retries < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    base_url = settings.HACKER_NEWS_API_URL
                    url =  base_url + f"/item/{source_id}.json"
                    res = await session.get(url=url)
                    item = None
                    
                    if res.status >= 200 and res.status < 300:
                        item = await res.json()
                    return item
            except aiohttp.ClientConnectorError:
                time.sleep(2)
                return await BaseModel.retrieve_data(source_id, retries+1)


    def get_model_type(self) -> models.Model:
        models = {
            "job": JobModel,
            "story": StoryModel,
            "comment": CommentModel,
            "poll": PollModel,
            "pollopt": PollOptionModel,
        }

        model_class = models.get(self.type)
        return model_class.objects.get(id=self.id)

    def get_kids(self) -> list:
        import ast
        if self.kids:
            kids = ast.literal_eval(self.kids)
        else:
            kids = []
        return kids

    def get_absolute_url(self) -> str:
        return reverse("site-app:retreive_items", kwargs={"id": self.id})
    

class JobModel(BaseModel):
    text = models.TextField(null=True)
    url = models.URLField(null=True)
    title = models.CharField(null=False, max_length=200)

    def save(self, *args, **kwargs) -> None:
        self.type = "job"
        super(JobModel, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    @staticmethod
    def get_Serializer_class() -> serializers.Serializer:
        from siteApp.serializers import JobModelSerializer
        return JobModelSerializer


class StoryModel(BaseModel):
    descendants = models.IntegerField(default=0)
    url = models.URLField(null=True)
    score = models.IntegerField(default=0, blank=True)
    title = models.CharField(null=False, max_length=200)

    def save(self, *args, **kwargs) -> None:
        self.type = "story"
        super(StoryModel, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    @staticmethod
    def get_Serializer_class():
        from siteApp.serializers import StoryModelSerializer
        return StoryModelSerializer


class CommentModel(BaseModel):
    parent = models.ForeignKey(BaseModel, on_delete=models.CASCADE, related_name="_parent")
    text = models.TextField(null=True, blank=True)

    def save(self, *args, **kwargs) -> None:
        self.type = "comment"
        super(CommentModel, self).save(*args, **kwargs)

    @staticmethod
    def get_Serializer_class() -> serializers.Serializer:
        from siteApp.serializers import CommentModelSerializer
        return CommentModelSerializer
    
    def get_absolute_url(self) -> str:
        return reverse("site-app:comment_detail", kwargs={"id": self.id})

    def get_replies(self):
        return CommentModel.objects.filter(parent=self)

class PollModel(BaseModel):
    descendants =  models.IntegerField(default=0, blank=True)
    score = models.IntegerField(default=0, blank=True)
    title = models.CharField(null=False, max_length=200)
    parts = ListField(null=True, blank=True)
    text = models.TextField(null=True, blank=True)

    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs) -> None:
        self.type = "poll"
        super(PollModel, self).save(*args, **kwargs)

    @staticmethod
    def get_Serializer_class():
        from siteApp.serializers import PollModelSerializer
        return PollModelSerializer

    def get_options(self):
        return PollOptionModel.objects.filter(parent=self).order_by("score")

class PollOptionModel(BaseModel):
    parent = models.ForeignKey(to=PollModel, on_delete=models.CASCADE)
    score = models.IntegerField(default=0, blank=True)
    title = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self) -> str:
        return f"option-{self.source_id}-on-{self.parent.title}"

    def save(self, *args, **kwargs) -> None:
        self.type = "pollopt"
        
        if not self.title:
            length = len(self.parent.polloptionmodel_set.all())
            self.title = f"option-{length+1}"
        
        super(PollOptionModel, self).save(*args, **kwargs)

    @staticmethod
    def get_Serializer_class():
        from siteApp.serializers import PollOptionModelSerializer
        return PollOptionModelSerializer


class UserModel(models.Model):
    source_id =  models.CharField(null=False, max_length=200, unique=True)
    delay = models.IntegerField(default=0)
    created = models.DateTimeField(default=timezone.now)
    karma = models.IntegerField(default=0)
    about = models.TextField(null=True, blank=True)
    submitted = ListField(null=True, blank=True)
    site_created = models.BooleanField(default=False)

    @staticmethod
    async def retrieve_data(user_id:str, retries=0) -> dict:
        if retries < 5:
            try:
                async with aiohttp.ClientSession() as session:
                    base_url = settings.HACKER_NEWS_API_URL
                    url = base_url + f"/user/{user_id}.json"
                    res = await session.get(url)
                    data =  None

                    if res.status >= 200 and res.status < 300:
                        data =  await res.json()
                    return data
            except aiohttp.ClientConnectorError:
                time.sleep(2)
                return await UserModel.retrieve_data(user_id, retries+1)

    @staticmethod
    async def create(source_id:str) -> models.Model:
        from siteApp.serializers import UserModelSerializer

        try:
            user = await sync_to_async(UserModel.objects.get)(source_id=source_id)
            return user
        except UserModel.DoesNotExist:
            user_data = await UserModel.retrieve_data(source_id)

            if user_data:
                serializer = UserModelSerializer(data=user_data)
                if serializer.is_valid():
                    user, _ = await sync_to_async(UserModel.objects.get_or_create)(**serializer.data)
                    return user


