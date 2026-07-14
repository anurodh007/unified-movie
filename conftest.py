"""
conftest.py - shared fixtures for the entire test

"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


"""
GLOBAL AUTOUSE: silence Pillow in User.save() for the entire session
"""
@pytest.fixture(autouse=True, scope='session')
def _patch_pillow_globally():
    mock_img = MagicMock()
    mock_img.height = 100
    mock_img.width = 100

    with patch('users.models.Image') as mock_image_module:
        mock_image_module.open.return_value = mock_img
        yield





"""
HELPERS
"""
# Create Access and Refresh Tokens
def make_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)





"""
CORE FIXTURES
"""

# Factory that creates user instances
@pytest.fixture
def user_factory(db):
    from django.contrib.auth import get_user_model
    User = get_user_model()

    def _create(username='testuser', password='StrongPass123!', email='test@example.com', **kwargs):
        return User.objects.create_user(username=username, password=password, email=email, **kwargs)
    
    return _create


# Single test user
@pytest.fixture
def user(user_factory):
    return user_factory(username='alice', email='alice@example.com')


# Another test user for ownership/permission tests
@pytest.fixture
def other_user(user_factory):
    return user_factory(username='bob', email='bob@example.com')


# Staff or Superuser
@pytest.fixture
def admin_user(user_factory):
    return user_factory(username='admin', email='admin@example.com', is_staff=True, is_superuser=True)


# Unauthenticated DRF APIClient
@pytest.fixture
def api_client():
    return APIClient()

# APIClient already authenticated as user via JWT
@pytest.fixture
def auth_client(api_client, user):
    access, _ = make_tokens(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
    return api_client

# Fresh APIClient authenticated as other_user
@pytest.fixture
def other_auth_client(other_user):
    client = APIClient()
    access, _ = make_tokens(other_user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
    return client





"""
DOMAIN FIXTURES
"""

# Factory that creates Genre instances
@pytest.fixture
def genre_factory(db):
    from movies.models import Genre

    def _create(tmdb_id=28, name='Action'):
        genre, _ = Genre.objects.get_or_create(
            tmdb_id=tmdb_id, defaults={'name': name}
        )
        return genre
    
    return _create

@pytest.fixture
def genre(genre_factory):
    return genre_factory()


# Factory that creates movie instances
@pytest.fixture
def movie_factory(db):
    from movies.models import Movie
    _counter = [1]

    def _create(tmdb_id=None, title='Test Movie', popularity=100.0, average_rating=0, vote_count=0, genres=None, **kwargs):
        if tmdb_id is None:
            tmdb_id = _counter[0] * 1000
            _counter[0] += 1
        
        movie, _ = Movie.objects.get_or_create(
            tmdb_id=tmdb_id,
            defaults={
                'title': title,
                'overview': 'A Test Movie',
                'popularity': popularity,
                'average_rating': average_rating,
                'vote_count': vote_count,
                **kwargs 
            }
        )

        if genres is not None:
            movie.genres.set(genres)
        return movie
    
    return _create

@pytest.fixture
def movie(movie_factory):
    return movie_factory(tmdb_id=550, title='Fight Club')


# Factory for StreamingPlatform Model
@pytest.fixture
def streaming_platform_factory(db):
    from movies.models import StreamingPlatform

    def _create(tmdb_id=8, name='Netflix', logo_path='/logo.png'):
        platform, _ = StreamingPlatform.objects.get_or_create(
            tmdb_id=tmdb_id, defaults={'name': name, 'logo_path': logo_path}
        )
        return platform
    
    return _create


# Factory for Review Model
@pytest.fixture
def review_factory(db):
    from reviews.models import Review

    def _create(user, movie, review_text='Nice film!', rating=7):
        review, _ = Review.objects.get_or_create(user=user, movie=movie, review_text=review_text, rating=rating)
        return review
    
    return _create

@pytest.fixture
def review(review_factory):
    return review_factory(user=user, movie=movie)


# Factory for Watchlist Model
@pytest.fixture
def watchlist_factory(db):
    from watchlist.models import Watchlist

    def _create(user, movie):
        wl, _ = Watchlist.objects.get_or_create(user=user, movie=movie)
        return wl
    
    return _create





"""
CONSTANTS
"""

@pytest.fixture
def fake_movie_detail():
    return {
        'id': 550,
        'title': 'Fight Club',
        'overview': 'An insomniac office worker and a devil-may-care soap maker...',
        'release_date': '1999-10-15',
        'runtime': 139,
        'popularity': 63.869,
        'poster_path': '/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
        'backdrop_path': '/87hTDiay2N2qWyX4Ds7ybXi9h8I.jpg',
        'genres': [
            {'id': 18, 'name': 'Drama'},
            {'id': 53, 'name': 'Thriller'},
        ],
    }

@pytest.fixture
def fake_search_response():
    return {
        'results': [
            {
                'id': 550,
                'title': 'Fight Club',
                'popularity': 63.869,
                'poster_path': '/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg',
            },
            {
                'id': 551,
                'title': 'Fight Club 2',
                'popularity': 10.0,
                'poster_path': None,
            },
        ]
    }

@pytest.fixture
def fake_trending_response():
    return {
        'results': [
            {'id': 100, 'title': 'Trending Movie', 'popularity': 200.0,
            'poster_path': '/abc.jpg'},
        ]
    }

@pytest.fixture
def fake_streaming_response():
    return  {
        'results': {
            'US': {
                'flatrate': [{'provider_id': 8, 'provider_name': 'Netflix'}],
            }
        }
    }