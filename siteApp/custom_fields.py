import ast
from rest_framework import serializers
from datetime import datetime
from django.db import models



class ListField(models.TextField):
    __metaclass__ = models.Field
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value
        
        try:
            r = ast.literal_eval(value)
        except:
            r = []
        
        return r

    def get_prep_value(self, value):
        if value is None:
            return value

        return str(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)


class UnixTimeField(serializers.Field):
    def to_representation(self, obj):
        return obj.isoformat()

    def to_internal_value(self, data):
        return datetime.utcfromtimestamp(data)
