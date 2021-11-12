from django.urls.conf import path

from .views import (
    item_list_create_views,
    item_retrieve_update_delete_views,
)

urlpatterns = [
    path("items/", item_list_create_views, name="list-items"),
    path("items/<int:id>/", item_retrieve_update_delete_views, name="retrieve-item-"),
]


