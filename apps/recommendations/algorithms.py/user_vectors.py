import numpy as np
from reviews.models import Review
from movie_vectors import (
    get_master_genre_list,
    build_movie_vector
)


def build_user_vector(user):
    """
    Builds a user-preference vector using highly rated movies
    """

    master_genres = get_master_genre_list()

    reviews = (
        Review.objects
        .filter(user=user, rating__gte=7)
        .select_related('movie')
    )

    if not reviews.exists():
        return np.zeros(len(master_genres), dtype=np.float32)
    
    vectors = []

    for review in reviews:
        vector = build_movie_vector(review.movie, master_genres)
        vectors.append(vector)

    user_vector = np.mean(vectors, axis=0)
    return user_vector