from django.db import models


class Genre(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    

class Movie(models.Model):
    tmdb_id = models.BigIntegerField(unique=True, db_index=True)
    
    title = models.CharField(max_length=255)
    overview = models.TextField(blank=True)

    release_date = models.DateField(null=True, blank=True)
    runtime = models.IntegerField(null=True, blank=True)

    poster_path = models.CharField(max_length=255, blank=True)
    backdrop_path = models.CharField(max_length=255, blank=True)

    popularity = models.FloatField(default=0)
    average_rating = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)

    genres = models.ManyToManyField(Genre, related_name='movies')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

class StreamingPlatform(models.Model):
    tmdb_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    logo_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name