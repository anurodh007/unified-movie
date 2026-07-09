from django.core.cache import cache
import numpy as np
from movies.models import Movie, Genre


def get_master_genre_list():
    """
    Returns all genres ordered alphabetically
    """
    return list(
        Genre.objects.order_by('name').values_list('name', flat=True)
    )


def build_movie_vector(movie, master_genres):
    """
    Converts a movie into binary NumPy vector
    """
    vector = np.zeros(len(master_genres), dtype=np.int8)

    movie_genres = set(
        movie.genres.values_list('name', flat=True)
    )

    for i, genre in enumerate(movie_genres):
        if genre in master_genres:
            vector[i] = 1

    return vector


def build_all_movie_vectors():
    """
    Builds vector for each movie
    """
    
    cache_key = 'movie_vectors'

    movie_vectors = cache.get(cache_key)
    if movie_vectors is not None:
        return movie_vectors

    master_genres = get_master_genre_list()

    movie_vectors = {}

    movies = Movie.objects.prefetch_related('genres')

    for movie in movies:
        movie_vectors[movie.tmdb_id] = {
            'movie': movie,
            'vector': build_movie_vector(movie, master_genres)
        }

    cache.set(cache_key, movie_vectors, 60 * 60)
    return movie_vectors