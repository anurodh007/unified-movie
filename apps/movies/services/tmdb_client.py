import requests
from requests.exceptions import RequestException
from config.env import env


API_KEY = env('API_KEY')
BASE_URL = env('TMDB_BASE_URL')
PARAMS = {
    'api_key': API_KEY,
    'language': 'en-US'
}


"""
GET movie details by tmdb_id
"""
def get_movie_details(tmdb_id):
    endpoint = f'{BASE_URL}/movie/{tmdb_id}'

    try:
        response = requests.get(endpoint, params=PARAMS)
        response.raise_for_status()
        return response.json()
    except RequestException:
        return None


"""
SEARCH movies by original, translated or alternative titles
"""
def search_movies_tmdb(query):
    endpoint = f'{BASE_URL}/search/movie'
    PARAMS['query'] = query

    try:
        response = requests.get(endpoint, params=PARAMS)
        response.raise_for_status()
        return response.json()
    except RequestException:
        return None


"""
Retrieve streaming details for movie with tmdb_id
"""
def get_streaming_details(tmdb_id):
    endpoint = f'{BASE_URL}/movie/{tmdb_id}/watch/providers'

    try:
        response = requests.get(endpoint, params=PARAMS)
        response.raise_for_status()
        return response.json()
    except RequestException:
        return None