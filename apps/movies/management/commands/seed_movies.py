import requests
from django.core.management.base import BaseCommand
from config.env import env
from movies.models import Movie, Genre

API_KEY = env('API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'


class Command(BaseCommand):
    help = 'Seed movies in database'

    def handle(self, *args, **kwargs):
        pages = 3

        """
        GET trending movies (week)
        """
        try:
            count = 0
            for page in range(1, pages + 1):
                endpoint = f'{BASE_URL}/trending/movie/week'
                params = {
                    'api_key': API_KEY,
                    'language': 'en-US',
                    'page': page
                }
                print(f'\nFetching page {page}...')
                response = requests.get(endpoint, params=params)

                if response.status_code == 200:
                    data = response.json()
                    movies = data.get('results', [])

                    for item in movies:
                        movie, created = Movie.objects.update_or_create(
                            tmdb_id=item['id'],
                            defaults={
                                'title': item['title'],
                                'overview': item['overview'],
                                'release_date': item['release_date'],
                                'poster_path': item['poster_path'],
                                'backdrop_path': item['backdrop_path'],
                                'popularity': item['popularity'],
                            }
                        )
                        genre_ids = item['genre_ids']
                        if genre_ids:
                            existing_genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                            movie.genres.set(existing_genres)

                        action = "Created" if created else "Updated"
                        print(f'[{action}] {movie.title}')

                        if not created:
                            count += 1
            
            print(f'Seeding complete: Updated {count} movies')

        except requests.exceptions.RequestException as e:
            print(self.style.ERROR(f'Error conecting to TMDB: {e}'))


        """
        GET popular movies
        """
        try:
            total_created = 0
            total_updated = 0
            for page in range(1, pages + 1):
                endpoint = f'{BASE_URL}/movie/popular'
                params = {
                    'api_key': API_KEY,
                    'language': 'en-US',
                    'page': page
                }
                print(f'\nFetching page {page}...')
                response = requests.get(endpoint, params=params)

                if response.status_code == 200:
                    data = response.json()
                    movies = data.get('results', [])

                    for item in movies:
                        movie, created = Movie.objects.update_or_create(
                            tmdb_id=item['id'],
                            defaults={
                                'title': item.get('title', ''),
                                'overview': item.get('overview', ''),
                                'release_date': item.get('release_date') or None,
                                'poster_path': item.get('poster_path') or '',
                                'backdrop_path': item.get('backdrop_path') or '',
                                'popularity': item.get('popularity', 0),
                            }
                        )
                        genre_ids = item.get('genre_ids', [])
                        if genre_ids:
                            existing_genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                            movie.genres.set(existing_genres)

                        action = "Created" if created else "Updated"
                        print(f'[{action}] {movie.title}')

                        if created:
                            total_created += 1
                        else:
                            total_updated += 1
            
            print(f'Seeding complete: Created {total_created} movies, Updated {total_updated} movies')

        except requests.exceptions.RequestException as e:
            print(self.style.ERROR(f'Error conecting to TMDB: {e}'))


        """
        GET top-rated movies
        """
        try:
            total_created = 0
            total_updated = 0
            for page in range(1, pages + 1):
                endpoint = f'{BASE_URL}/movie/top_rated'
                params = {
                    'api_key': API_KEY,
                    'language': 'en-US',
                    'page': page
                }
                print(f'\nFetching page {page}...')
                response = requests.get(endpoint, params=params)

                if response.status_code == 200:
                    data = response.json()
                    movies = data.get('results', [])

                    for item in movies:
                        movie, created = Movie.objects.update_or_create(
                            tmdb_id=item['id'],
                            defaults={
                                'title': item.get('title', ''),
                                'overview': item.get('overview', ''),
                                'release_date': item.get('release_date') or None,
                                'poster_path': item.get('poster_path') or '',
                                'backdrop_path': item.get('backdrop_path') or '',
                                'popularity': item.get('popularity', 0),
                            }
                        )
                        genre_ids = item.get('genre_ids', [])
                        if genre_ids:
                            existing_genres = Genre.objects.filter(tmdb_id__in=genre_ids)
                            movie.genres.set(existing_genres)

                        action = "Created" if created else "Updated"
                        print(f'[{action}] {movie.title}')

                        if created:
                            total_created += 1
                        else:
                            total_updated += 1
            
            print(f'Seeding complete: Created {total_created} movies, Updated {total_updated} movies')

        except requests.exceptions.RequestException as e:
            print(self.style.ERROR(f'Error conecting to TMDB: {e}'))


        """
        UPDATE runtime
        """
        movies = Movie.objects.all()
        count = 0

        for m in movies:
            try:
                endpoint = f'{BASE_URL}/movie/{m.tmdb_id}'
                params = {
                    'api_key': API_KEY,
                    'language': 'en-US',
                }

                response = requests.get(endpoint, params=params)
                if response.status_code == 200:
                    data =response.json()
                    id = data.get('id')
                    runtime = data.get('runtime') or None
                    Movie.objects.filter(tmdb_id=id).update(runtime=runtime)
                    count += 1

            
            except requests.exceptions.RequestException as e:
                print(self.style.ERROR(f'Error conecting to TMDB: {e}'))

        print(f'Updated {count} movies')