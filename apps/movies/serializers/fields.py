from rest_framework import serializers
from config.env import env


IMAGE_BASE_URL = env('TMDB_IMAGE_BASE_URL')
IMAGE_SIZE = 'w500'


"""
Custom Field to build image path 
"""
class TMDBImageField(serializers.Field):
    def to_representation(self, value):
        return f'{IMAGE_BASE_URL}/{IMAGE_SIZE}{value}' if value else ''