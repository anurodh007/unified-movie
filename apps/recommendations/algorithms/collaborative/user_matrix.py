import numpy as np

from django.core.cache import cache
from django.contrib.auth import get_user_model

from movies.models import Movie
from reviews.models import Review

User = get_user_model()

CACHE_KEY = 'user_movie_matrix'
CACHE_TIMEOUT = 60 * 60 * 12


def build_user_matrix():
    """
    Builds a user matrix where rows = users and cols = movies and values are ratings

    Returns
    {
        'matrix': matrix,
        'user_index': user_index,
        'movie_index': movie_index
    }
    """

    matrix_data = cache.get(CACHE_KEY)
    if matrix_data is not None:
        return matrix_data
    
    # Retrieve users who have at least one review
    users = (
        User.objects
        .filter(user_reviews__isnull=False)
        .distinct()
        .order_by('id')
    )

    # Retrieve reviewed movies only
    movies = (
        Movie.objects
        .filter(movie_reviews__isnull=False)
        .distinct()
        .order_by('tmdb_id')
    )

    # Create index mappings
    user_index = {
        user.id: idx for idx, user in enumerate(users)
    }

    movie_index = {
        movie.tmdb_id: idx for idx, movie in enumerate(movies)
    }

    # Create rating matrix
    matrix = np.zeros(
        (len(user_index), len(movie_index)),
        dtype=np.float32
    )

    reviews = (
        Review.objects
        .select_related('user', 'movie')
        .only('rating', 'user__id', 'movie__tmdb_id')
    )

    for review in reviews:
        row = user_index[review.user_id]
        col = movie_index[review.movie.tmdb_id]

        matrix[row, col] = review.rating

    matrix_data = {
        'matrix': matrix,
        'user_index': user_index,
        'movie_index': movie_index
    }

    cache.set(CACHE_KEY, matrix_data, CACHE_TIMEOUT)

    return matrix_data