"""
Tests JWT Tokens

Endpoint under test:

POST /api/auth/login/
POST /api/auth/refresh/
"""

import pytest
from datetime import timedelta
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

LOGIN_URL = '/api/auth/login/'
REFRESH_URL = '/api/auth/refresh/'



"""
JWT Token Tests
"""
@pytest.mark.django_db
class TestJWTTokens:

    def test_access_token_is_non_empty_string(self, api_client, user_factory):
        user_factory(username='jwtuser', password='StrongPass123!')
        response = api_client.post(
            LOGIN_URL,
            {'username': 'jwtuser', 'password': 'StrongPass123!'},
            format='json'
        )
        assert isinstance(response.data['access'], str)
        assert len(response.data['access']) > 50

    def test_refresh_token_produces_new_access_token(self, api_client, user_factory):
        user_factory(username='jwtuser', password='StrongPass123!')
        response = api_client.post(
            LOGIN_URL,
            {'username': 'jwtuser', 'password': 'StrongPass123!'},
            format='json'
        )
        refresh_token = response.data['refresh']
        response = api_client.post(REFRESH_URL, {'refresh': refresh_token}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_invalid_access_token_returns_401(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_invalid_refresh_token_returns_401(self, api_client):
        response = api_client.post(REFRESH_URL, {'refresh': 'invalid-token'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_malformed_auth_header_returns_401(self, api_client):
        api_client.credentials(HTTP_AUTHORIZATION='Token access-token')
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_no_auth_returns_401(self, api_client):
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_expired_access_token_returns_401(self, api_client, user):
        token = AccessToken.for_user(user=user)
        token.set_exp(lifetime=timedelta(seconds=-1))
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token)}')
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_used_as_access_returns_401(self, api_client, user):
        token = RefreshToken.for_user(user=user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(token)}')
        response = api_client.get('/api/recommendations/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED