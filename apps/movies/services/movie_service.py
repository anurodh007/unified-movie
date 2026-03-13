from movies.models import Movie, Genre
from movies.services.tmdb_client import get_movie_details


"""
Retrive movie from db if exists else API call to TMDB and store
"""
def get_or_create_movie(tmdb_id):
    movie = Movie.objects.filter(tmdb_id=tmdb_id).first()

    if not movie:
        # Fetch from TMDB if movie doesn't exist
        data = get_movie_details(tmdb_id=tmdb_id)

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
    
    return movie