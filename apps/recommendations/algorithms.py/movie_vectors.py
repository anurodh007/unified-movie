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
    
    master_genres = get_master_genre_list()

    movie_vectors = {}

    movies = Movie.objects.prefetch_related('genres')

    for movie in movies:
        movie_vectors[movie.tmdb_id] = build_movie_vector(movie, master_genres)

    return movie_vectors