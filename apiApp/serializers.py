from django.db import models
from rest_framework import serializers

from siteApp.models import (
    CommentModel, JobModel, PollModel,PollOptionModel,
    BaseModel, StoryModel, UserModel,
)



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        exclude = ['source_id']


class ItemSerializer(serializers.ModelSerializer):
    by = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = BaseModel
        exclude = ['source_id']
        depth = 1

class JobSerializer(serializers.ModelSerializer):
    by = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = JobModel
        exclude = ['source_id']
        depth = 1

class StorySerializer(serializers.ModelSerializer):
    by = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = StoryModel
        exclude = ['source_id']
        depth = 1


class CommentSerializer(serializers.ModelSerializer):
    by = serializers.PrimaryKeyRelatedField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=BaseModel.objects.all())
    class Meta:
        model = CommentModel
        exclude = ['source_id']
        depth = 1


class PollSerializer(serializers.ModelSerializer):
    by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PollModel
        exclude = ['source_id']
        depth = 1


class PollOptionSerializer(serializers.ModelSerializer):
    by = serializers.PrimaryKeyRelatedField(read_only=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=BaseModel.objects.all())

    class Meta:
        model = PollOptionModel
        exclude = ['source_id']
        depth = 1
