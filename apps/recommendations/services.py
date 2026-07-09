from .algorithms.user_vectors import build_user_vector
from .algorithms.movie_vectors import build_all_movie_vectors
from .algorithms.similarity import calculate_similarity
from .algorithms.ranking import rank_filter_recommendations


def get_recommendations(user, limit=10):
    """
    Build movie vectors and user vector
    Compute similarity score
    Rank and filter movies
    Return recommendation
    """

    movie_vectors = build_all_movie_vectors()

    user_vector = build_user_vector(user)

    similarity_scores = calculate_similarity(user, user_vector, movie_vectors)

    return rank_filter_recommendations(user, similarity_scores, limit)