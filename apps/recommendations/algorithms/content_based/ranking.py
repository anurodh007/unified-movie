from reviews.models import Review
from watchlist.models import Watchlist


def rank_filter_recommendations(user, scores, limit=10):
    """
    Ranks similarity scores from highest to lowest.
    Filters out movies already reviewed or in watchlist.
    Returns top N recommendations.
    """

    # Sort the similarity score
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

    for tmdb_id, item in sorted_scores.items():
        if int(tmdb_id) in excluded_ids:
            continue
        
        recommendations.append({
            'tmdb_id': int(tmdb_id),
            'movie': item['movie'],
            'score': item['score']
        })
        
        if len(recommendations) == limit:
            break

    return recommendations