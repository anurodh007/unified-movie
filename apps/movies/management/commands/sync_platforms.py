import requests
from django.core.management.base import BaseCommand
from config.env import env
from movies.models import StreamingPlatform


API_KEY = env('API_KEY')
BASE_URL = env('TMDB_BASE_URL')


class Command(BaseCommand):
    help = 'Add streaming platforms metadata to database'

    def handle(self, *args, **kwargs):
        endpoint = f'{BASE_URL}/watch/providers/movie'
        params = {
            'api_key': API_KEY,
            'lamguage': 'en-US'
        }

        try:
            response = requests.get(endpoint, params=params)
            
            total_created = 0
            total_updated = 0
            if response.status_code == 200:
                data = response.json()
                platforms = data.get('results', [])

                for item in platforms:
                    platform, created = StreamingPlatform.objects.update_or_create(
                        tmdb_id=item['provider_id'],
                        defaults={
                            'name': item.get('provider_name', ''),
                            'logo_path': item.get('logo_path') or '',
                        }
                    )

                    if created:
                        total_created += 1
                    else:
                        total_updated += 1

            print(f'Sync complete: Created {total_created} platforms, Updated {total_updated} platforms')

        except requests.exceptions.RequestException as e:
            print(self.style.ERROR(f'Error connecting to TMDB: {e}'))