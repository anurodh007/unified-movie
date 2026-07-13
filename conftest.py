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





"""
DOMAIN FIXTURES
"""

# Factory that creates Genre instances
@pytest.fixture
def genre_factory(db):
    from apps.movies.models import Genre

    def _create(tmdb_id=28, name='Action'):
        genre, _ = Genre.objects.get_or_create(
            tmdb_id=tmdb_id, defaults={'name': name}
        )
        return genre
    
    return _create

@pytest.fixture
def genre(genre_factory):
    return genre_factory()





"""
CONSTANTS
"""