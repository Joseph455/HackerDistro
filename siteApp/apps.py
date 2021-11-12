from django.apps import AppConfig
from django.conf import settings
import threading

class SiteappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'siteApp'
