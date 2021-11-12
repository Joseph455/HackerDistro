from rest_framework import serializers

from .custom_fields import UnixTimeField

from .models import BaseModel, UserModel


class BaseModelSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    deleted = serializers.BooleanField(required=False)
    type = serializers.CharField(required=False)
    by = serializers.CharField(required=False)
    time = UnixTimeField(required=False)
    dead = serializers.BooleanField(required=False)
    kids = serializers.ListField(required=False)

    @property
    async def data(self) -> dict:
        data = super(BaseModelSerializer, self).data

        if not data.get("source_id"):
            data["source_id"] = data.get("id")
        
        if data.get("id"):
            del data["id"]

        return await self.process_data(data)

    async def process_data(self, data) -> dict:
        by = await UserModel.create(data.get('by'))
        data.update({"by": by})
        return data


class JobModelSerializer(BaseModelSerializer):
    text = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
    title = serializers.CharField(required=False)


class StoryModelSerializer(BaseModelSerializer):
    descendants = serializers.IntegerField(required=False, default=0)
    url = serializers.URLField(required=False)
    score = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=200, required=False)


class CommentModelSerializer(BaseModelSerializer):
    parent = serializers.IntegerField(required=False)
    text = serializers.CharField(required=False)

    async def process_data(self, data:dict) -> dict:
        by = await UserModel.create(data.get('by'))
        data.update({"by": by})

        parent, _ = await BaseModel.create(data.get('parent'))
        data.update({"parent": parent})
        return data

class PollModelSerializer(BaseModelSerializer):
    descendants =  serializers.IntegerField(required=False)
    score = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=200, required=False)
    text = serializers.CharField(required=False)


class PollOptionModelSerializer(CommentModelSerializer):
    score = serializers.IntegerField(required=False)
    text = None


class UserModelSerializer(serializers.Serializer):
    id =  serializers.CharField(max_length=200, required=False)
    delay = serializers.IntegerField(required=False)
    created = UnixTimeField(required=False)
    karma = serializers.IntegerField(required=False)
    about = serializers.CharField(required=False)
    submitted = serializers.ListField(required=False)

    @property
    def data(self):
        data = super(UserModelSerializer, self).data

        if not data.get("source_id"):
            data["source_id"] = data.get("id")
            del data["id"]
        return data

