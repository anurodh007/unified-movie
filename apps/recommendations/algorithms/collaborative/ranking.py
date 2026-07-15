from movies.models import Movie


def rank_recommendations(predicted_ratings, limit=10):
    """
    Sort prediction scores and return N recommendations
    """

    # Sort predicted ratings
    sorted_ratings = sorted(predicted_ratings.items(), key=lambda item: item[1], reverse=True)

    tmdb_ids = predicted_ratings.keys()

    movies = Movie.objects.filter(tmdb_id__in=tmdb_ids)

    movie_lookup = {
        movie.tmdb_id: movie for movie in movies
    }

    # Convert tmdb_id into movie objects
    recommendations = []

    for tmdb_id, rating in sorted_ratings:
        movie = movie_lookup.get(tmdb_id)

        if movie is None:
            continue

        recommendations.append({
            'tmdb_id': int(tmdb_id),
            'movie': movie,
            'score': rating,
            'recommendation_type': 'collaborative'
        })

        if len(recommendations) == limit:
            break
    
    return recommendations