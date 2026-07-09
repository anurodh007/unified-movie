from reviews.models import Review
from watchlist.models import Watchlist

from .similarity import calculate_similarity


def rank_filter_recommendations(user, limit=10):
    """
    Ranks similarity scores from highest to lowest.
    Filters out movies already reviewed or in watchlist.
    Returns top N recommendations.
    """

    scores = calculate_similarity(user)

    # Sort by similarity score
    sorted_scores = dict(sorted(scores.items(), key=lambda item: item[1]['score'], reverse=True))

    # Get reviewed and watchlisted IDs
    reviewed_ids = set(
        Review.objects.filter(user=user)
        .values_list('movie__tmdb_id', flat=True)
    )
    watchlisted_ids = set(
        Watchlist.objects.filter(user=user)
        .values_list('movie__tmdb_id', flat=True)
    )
    excluded_ids = reviewed_ids | watchlisted_ids

    recommendations = []

    for item in sorted_scores:
        if item['movie'].tmdb_id in excluded_ids:
            continue
        
        recommendations.append(item)
        if len(recommendations == limit):
            break

    return recommendations