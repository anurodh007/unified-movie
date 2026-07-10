import numpy as np
from numpy.linalg import norm

from django.core.cache import cache

CACHE_TIMEOUT = 60 * 60 * 12


def calculate_similarity(user, user_matrix):
    """
    Calculates user-to-user cosine similarity

    Returns
    {
        user_id: similarity,
    }
    """

    cache_key = f'user_similarity_{user.id}'
    scores = cache.get(cache_key)
    if scores is not None:
        return scores

    matrix = user_matrix.get('matrix')
    user_index = user_matrix.get('user_index')

    reverse_index = {idx: user_id for user_id, idx in user_index.items()}

    current_user_index = user_index.get(user.id)
    if current_user_index is None:
        return {}

    current_user_vector = matrix[current_user_index]

    norm_current = norm(current_user_vector)

    scores = {}

    for idx, row in enumerate(matrix):
        if idx == current_user_index:
            continue

        norm_row = norm(row)

        if np.isclose(norm_current, 0) or np.isclose(norm_row, 0):
            similarity = 0  
        else:
            similarity = np.dot(current_user_vector, row) \
                            / (norm_current * norm_row)
            
        user_id = reverse_index[idx]
        scores[user_id] = similarity

    cache.set(cache_key, scores, CACHE_TIMEOUT)
    return scores