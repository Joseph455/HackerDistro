from django.db.models.base import Model
from django.db.models.query import QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.serializers import Serializer

from rest_framework.viewsets import ViewSetMixin
from rest_framework.decorators import action
from rest_framework.views import Response, status
from rest_framework.generics import GenericAPIView

from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import (
    CommentSerializer,
    ItemSerializer, 
    JobSerializer, 
    PollOptionSerializer, 
    PollSerializer, 
    StorySerializer
)

from siteApp.models import (
    BaseModel,
    JobModel,
    StoryModel,
    CommentModel,
    PollModel,
    PollOptionModel,
    UserModel
)




class NewsViewset(ViewSetMixin, GenericAPIView):
    queryset = BaseModel.objects.all()
    serializer_class = ItemSerializer
    filter_backends=[DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['site_created', 'type', 'deleted', 'time']
    ordering_fields = ['time', 'kids']


    def get_queryset(self):
        query = super(NewsViewset, self).get_queryset()
        query = self.filter_queryset(query)
        return query

    def get_object(self, id:int):
        # modified to return the instance and its serializer class
        try:
            base_item_instance = BaseModel.objects.get(id=id)

            types = {
                "job": [JobModel, JobSerializer],
                "story": [StoryModel, StorySerializer],
                "comment": [CommentModel, CommentSerializer],
                "poll": [PollModel, PollSerializer],
                "pollopt": [PollOptionModel, PollOptionSerializer],
            }

            model_class, serializer_class = types.get(base_item_instance.type, [None, None])

            instance = model_class.objects.get(id=id)
            return instance, serializer_class
        except BaseModel.DoesNotExist:
            return None, None


    @swagger_auto_schema(
        operation_id="create-item",
        responses={
            200: ItemSerializer,
            404: "Not found",
        },
    )
    @action(
        methods=["POST"],
        detail=True,
    )
    def create_item(self, request, *args, **kwargs):
        base_serializer = ItemSerializer(data=request.data)
        base_serializer.save
        if base_serializer.is_valid():
            types = {
                "job": JobSerializer,
                "story": StorySerializer,
                "comment": CommentSerializer,
                "poll": PollSerializer,
                "pollopt": PollOptionSerializer,
            }
            serializer_class = types.get(base_serializer.data.get("type"), base_serializer)
            serializer = serializer_class(data=base_serializer.initial_data)
            serializer.is_valid(raise_exception=True)
            data =  dict(base_serializer.initial_data)
            by = UserModel.objects.get(id=data.get("by"))
            serializer.save(by=by)
            return Response(serializer.data, status=201)
        else:
            return Response(base_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(
        operation_id="list-items",
        responses={
            200: ItemSerializer,
            404: "Not found",
        },
    )
    @action(
        methods=["GET"],
        detail=False,
    )
    def list_items(self, request, *args, **kwargs):
        query = self.get_queryset()
        query = self.paginate_queryset(query)
        serializer = ItemSerializer(instance=query, many=True)
        return Response(data=serializer.data)
    
    @swagger_auto_schema(
        operation_id="retrieve-item",
        responses={
            200: ItemSerializer,
            404: "Not found",
        },
    )
    @action(
        methods=["GET"],
        detail=True,
    )
    def retrieve_item(self, request, id:int, *args, **kwargs):
        instance, serializer_class = self.get_object(id)
        if instance and serializer_class:
            serializer = serializer_class(instance=instance)
            return Response(data=serializer.data)
        else:
            error_msg = {"error": "Not found"}
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_id="update-item",
        responses={
            200: ItemSerializer,
            404: "Not found",
        },
    )
    @action(
        methods=["PUT"],
        detail=True,
    )
    def update_item(self, request, id:int, *args, **kwargs):
        instance, serializer_class = self.get_object(id)
        if instance and serializer_class:
            serializer = serializer_class(instance=instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.update(instance, validated_data=serializer.validated_data)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            error_msg = {"error": "Not found"}
            return Response(error_msg, status=404)


    @swagger_auto_schema(
        operation_id="delete-item",
        responses={
            200: ItemSerializer,
            404: "Not found",
        },
    )
    @action(
        methods=["DELETE"],
        detail=True,
    )
    def delete_item(self, request, id:int, *args, **kwargs):
        instance, _ = self.get_object(id)
        if instance:
            if instance.site_created:
                instance.delete()
                return Response(status=204)
            else:
                return Response({'error': 'cant delete item'}, status=status.HTTP_403_FORBIDDEN)
        else:
            error_msg = {"error": "Not found"}
            return Response(error_msg, status=status.HTTP_404_NOT_FOUND)


item_list_create_views = NewsViewset.as_view(
    {
        "get": "list_items",
        "post": "create_item",
    }
)

item_retrieve_update_delete_views = NewsViewset.as_view(
    {
        "get": "retrieve_item",
        "put": "update_item",
        "delete": "delete_item"
    }
)