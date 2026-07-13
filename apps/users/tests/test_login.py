"""
Tests for user login

Endpoint under test:

POST /api/auth/login/
"""

import pytest
from rest_framework import status

LOGIN_URL = '/api/auth/login/'



"""
Login Tests
"""
@pytest.mark.django_db
class TestLogin:

    def test_login_with_valid_credentials_returns_200(self, api_client, user_factory):
        user_factory(username='loginuser', password='StrongPass123!')
        response = api_client.post(
            LOGIN_URL,
            {'username': 'loginuser', 'password': 'StrongPass123!'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK

    def test_login_with_incorrect_password_returns_401(self, api_client, user_factory):
        user_factory(username='loginuser', password='StrongPass123!')
        response = api_client.post(
            LOGIN_URL,
            {'username': 'loginuser', 'password': 'IncorrectPass'},
            format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_with_nonexistent_user_returns_401(self, api_client):
        response = api_client.post(
            LOGIN_URL,
            {'username': 'login', 'password': 'pass'},
            format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_with_missing_username_returns_400(self, api_client):
        response = api_client.post(LOGIN_URL, {'password': 'pass'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_missing_password_returns_400(self, api_client):
        response = api_client.post(LOGIN_URL, {'username': 'loginuser'}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_empty_values_returns_400(self, api_client):
        response = api_client.post(LOGIN_URL, {'username': '', 'password': ''}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_login_returns_access_and_refresh_tokens(self, api_client, user_factory):
        user_factory(username='loginuser', password='StrongPass123!')
        response = api_client.post(
            LOGIN_URL,
            {'username': 'loginuser', 'password': 'StrongPass123!'},
            format='json'
        )
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_excludes_password_in_response(self, api_client, user_factory):
        user_factory(username='loginuser', password='StrongPass123!')
        response = api_client.post(
            LOGIN_URL,
            {'username': 'loginuser', 'password': 'StrongPass123!'},
            format='json'
        )
        assert 'password' not in response.data