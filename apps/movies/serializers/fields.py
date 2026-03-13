from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from config.env import env


IMAGE_BASE_URL = env('TMDB_IMAGE_BASE_URL')
IMAGE_SIZE = 'w500'


"""
Custom Field to build image path 
"""
@extend_schema_field({'type': 'string', 'format': 'uri'})
class TMDBImageField(serializers.Field):
    def to_representation(self, value):
        return f'{IMAGE_BASE_URL}/{IMAGE_SIZE}{value}' if value else ''