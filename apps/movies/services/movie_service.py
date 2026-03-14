from django.core.cache import cache
from django.db import transaction
from django.db.models import Q
from movies.models import Movie, Genre, StreamingPlatform
from movies.services.tmdb_client import (
    get_movie_details,
    search_movies_tmdb,
    get_streaming_details,
    get_trending_movies_by_day
)


"""
Retrieve movie from db if exists else API call to TMDB and store
"""
def get_or_create_movie(tmdb_id):
    cache_key = f'movie_details_{tmdb_id}'
    movie = cache.get(cache_key)

    if movie:
        return movie
    
    movie = Movie.objects.filter(tmdb_id=tmdb_id).first()

    if not movie:
        # Fetch from TMDB if movie doesn't exist
        data = get_movie_details(tmdb_id=tmdb_id)
        if not data:
            return None

        with transaction.atomic():
            movie, _ = Movie.objects.update_or_create(
                tmdb_id=data.get('id'),
                defaults={
                    'title': data.get('title', ''),
                    'overview': data.get('overview', ''),
                    'release_date': data.get('release_date') or None,
                    'runtime': data.get('runtime', 0),
                    'popularity': data.get('popularity', 0),
                    'poster_path': data.get('poster_path') or '',
                    'backdrop_path': data.get('backdrop_path') or ''
                }
            )

            movie_genres = data.get('genres', [])
            if movie_genres:
                genre_instances = []
                for g in movie_genres:
                    # Sync genres before linking
                    genre_obj, _ = Genre.objects.get_or_create(
                        tmdb_id=g['id'],
                        defaults={'name': g.get('name', 'Unknown')}
                    )
                    genre_instances.append(genre_obj)
                movie.genres.set(genre_instances)

    cache.set(cache_key, movie, 60 * 60 * 6)
    return movie


"""
SEARCH movies in db if exists else API call to TMDB
"""
def search_movies(query):
    query = query.strip()
    cache_key = f'search_movies_{query}'
    movies = cache.get(cache_key)

    if movies:
        return movies

    movies = Movie.objects.filter(
        Q(title__icontains=query) | Q(overview__icontains=query)
    )
    # Return queryset if exists 3 or more
    if movies.count() >= 3:
        cache.set(cache_key, movies, 60 * 30)
        return movies
    
    data = search_movies_tmdb(query)
    if not data:
        return None

    results = data.get('results', [])
    movies_list = []
    for movie in results[:10]:
        movies_list.append({
            'tmdb_id': movie.get('id'),
            'title': movie.get('title', ''),
            'popularity': movie.get('popularity', 0),
            'poster_path': movie.get('poster_path') or None
        })

    cache.set(cache_key, movies_list, 60 * 30)
    return movies_list


"""
Retrieve streaming details for a movie
"""
def get_streaming_platforms(tmdb_id):
    cache_key = f'streaming_details_of_{tmdb_id}'
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    data = get_streaming_details(tmdb_id)
    if not data:
        return None

    results = data.get('results', {})
    us_data = results.get('US', {})

    provider_ids = {
        p.get('provider_id')
        for category in ['rent', 'flatrate', 'buy']
        for p in us_data.get(category, [])
    }

    platforms = StreamingPlatform.objects.filter(tmdb_id__in=list(provider_ids))
    cache.set(cache_key, platforms, 60 * 60 * 24)
    return platforms


"""
GET trending movies by week
"""
def get_trending_movies(page_num):
    cache_key = f'trending_movies_page_{page_num}'
    results = cache.get(cache_key)
    if results:
        return results

    data = get_trending_movies_by_day()
    if not data:
        return None
    
    results = data.get('results', [])
    api_movies_list = []

    for item in results:
        api_movies_list.append({
            'tmdb_id': item.get('id'),
            'title': item.get('title', ''),
            'popularity': item.get('popularity', 0),
            'poster_path': item.get('poster_path') or None
        })
    cache.set(cache_key, api_movies_list, 60 * 60 * 24)
    return api_movies_list