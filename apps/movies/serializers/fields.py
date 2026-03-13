from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from config.env import env


IMAGE_BASE_URL = env('TMDB_IMAGE_BASE_URL')
DEFAULT_SIZE = 'w500'


"""
Custom Generic Field to build image path 
"""
@extend_schema_field({'type': 'string', 'format': 'uri'})
class TMDBImageField(serializers.Field):
    def __init__(self, size=DEFAULT_SIZE, **kwargs):
        self.size = size
        super().__init__(**kwargs)

    def to_representation(self, value):
        if not value:
            return ''
        path = value if value.startswith('/') else f'/{value}'
        return f'{IMAGE_BASE_URL}/{self.size}{path}'