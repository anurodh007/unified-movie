import requests
from django.core.management.base import BaseCommand
from config.env import env
from movies.models import Genre


API_KEY = env('API_KEY')
BASE_URL = 'https://api.themoviedb.org/3'


class Command(BaseCommand):
    help = 'Sync movie genres from TMDB'

    def handle(self, *args, **kwargs):
        endpoint = f'{BASE_URL}/genre/movie/list'
        params = {
            'api_key': API_KEY,
            'language': 'en-US',
        }

        try:
            response = requests.get(endpoint, params=params)
            data = response.json()
            genres = data.get('genres', [])

            total_created = 0
            total_updated = 0
            for item in genres:
                genre, created = Genre.objects.update_or_create(
                    tmdb_id=item['id'],
                    defaults={'name': item['name']}
                )
                if created:
                    total_created += 1
                else:
                    total_updated += 1

            print(f'Sync complete: Created {total_created} genres, Updated {total_updated}')

        except requests.exceptions.RequestException as e:
            print(self.style.ERROR(f'Error connecting to TMDB: {e}'))