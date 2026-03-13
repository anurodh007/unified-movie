from rest_framework import serializers
from movies.models import StreamingPlatform
from movies.serializers.fields import TMDBImageField


class StreamingPlatformSerializer(serializers.ModelSerializer):
    logo_path = TMDBImageField(size='w92')

    class Meta:
        model = StreamingPlatform
        fields = [
            'tmdb_id',
            'name',
            'logo_path'
        ]