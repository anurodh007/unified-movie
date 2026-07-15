"""
Integration Tests for authentication workflow
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

REGISTER_URL = '/api/auth/register/'
LOGIN_URL = '/api/auth/login/'
REFRESH_URL = '/api/auth/refresh/'


@pytest.mark.django_db
class TestAuthenticationFlow:

    def test_register_login_access_profile_logout(self):
        register_data = {
            'username': 'newuser',
            'email': 'newuser@mail.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        }

        client = APIClient()
        response = client.post(REGISTER_URL, register_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@mail.com'

        response = client.post(LOGIN_URL, {'username': 'newuser', 'password': 'StrongPass123!'}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        access_token = response.data['access']
        refresh_token = response.data['refresh']

        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = client.get('/api/users/newuser/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'newuser'
        assert response.data['email'] == 'newuser@mail.com'

        response = client.patch('/api/users/newuser/', {'bio': 'I am a new user.'}, format='json')
        assert response.data['bio'] == 'I am a new user.'