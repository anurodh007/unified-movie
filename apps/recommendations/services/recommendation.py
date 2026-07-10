from reviews.models import Review

from .content_based import get_recommendations_content
from .collaborative import get_recommendations_collab

MINIMUM_REVIEWS = 5


def get_recommendations(user, limit=10):
    """
    Chooses recommendation algorithm based on user activity
    """

    review_count = Review.objects.filter(user=user).count()

    if review_count <= MINIMUM_REVIEWS:
        return get_recommendations_content(user, limit)
    

    recommendations = get_recommendations_collab(user, limit)
    if recommendations:
        return recommendations
    
    return get_recommendations_content(user, limit)