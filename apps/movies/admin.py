from django.contrib import admin
from movies.models import Genre, Movie


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['tmdb_id', 'name']


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    ...