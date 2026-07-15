from ..algorithms.collaborative.user_matrix import build_user_matrix
from ..algorithms.collaborative.similarity import calculate_similarity
from ..algorithms.collaborative.prediction import predict_movie_ratings
from ..algorithms.collaborative.ranking import rank_recommendations


def get_recommendations_collab(user, limit=10):
    
    user_matrix = build_user_matrix()

    similarity_scores = calculate_similarity(user, user_matrix)

    predicted_ratings = predict_movie_ratings(user, user_matrix, similarity_scores, k=3)

    return rank_recommendations(predicted_ratings, limit=limit)