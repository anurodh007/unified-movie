from django.core.cache import cache

CACHE_TIMEOUT = 60 * 60 * 12


def predict_movie_ratings(user, user_matrix, similarity_scores, k=5):
    """
    Predict how much user likes a movie they haven't rated.

    Returns
    {
        tmdb_id: predicted_rating
    }
    """

    cache_key = f'predicted_ratings_{user.id}'
    predicted_ratings = cache.get(cache_key)
    if predicted_ratings is not None:
        return predicted_ratings

    # Sort users by similarity scores
    sorted_scores = sorted(similarity_scores.items(), key=lambda item: item[1], reverse=True)[:k]

    matrix = user_matrix.get('matrix')
    user_index = user_matrix.get('user_index')
    movie_index = user_matrix.get('movie_index')
    reverse_movie_index = {
        idx: tmdb_id for tmdb_id, idx in movie_index.items()
    }

    # Get current user index and vector
    current_user_index = user_index.get(user.id)
    if current_user_index is None:
        return {}
    current_user_vector = matrix[current_user_index]

    # Predict ratings
    predicted_ratings = {}

    for col, current_rating in enumerate(current_user_vector):
        if current_rating != 0:
            continue
        
        sum_product = 0
        sum_similarity = 0

        for i in range(k):
            row = user_index[sorted_scores[i][0]]
            if row is None:
                continue

            rating = matrix[row][col]
            if rating == 0:
                continue

            similarity = sorted_scores[i][1]
            if similarity <= 0:
                continue

            sum_product += similarity * rating
            sum_similarity += similarity

        if sum_similarity == 0:
            predicted = 0
        else:
            predicted = sum_product / sum_similarity

        tmdb_id = reverse_movie_index[col]

        predicted_ratings[tmdb_id] = predicted

    cache.set(cache_key, predicted_ratings, CACHE_TIMEOUT)
    return predicted_ratings