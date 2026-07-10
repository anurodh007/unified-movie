from django.core.cache import cache
import numpy as np
from numpy.linalg import norm


def calculate_similarity(user, user_vector, movie_vectors):
    """
    Calculate similarity scores between user and movie
    """

    cache_key = f'similarity_scores_{user.id}'
    scores = cache.get(cache_key)

    if scores is not None:
        return scores
    
    user_norm = norm(user_vector)

    scores = {}

    for tmdb_id, data in movie_vectors.items():
        movie_norm = data['norm']

        if user_norm == 0 or movie_norm == 0:
            similarity = 0.0
        else:
            similarity = np.dot(user_vector, data['vector'])\
                        / (user_norm * movie_norm)

        scores[tmdb_id] = {
            'movie': data['movie'],
            'score': similarity,
        }
        
    cache.set(cache_key, scores, 60 * 60 * 12)
    return scores