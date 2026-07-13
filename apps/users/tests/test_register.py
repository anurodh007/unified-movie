"""
Tests for user registration

Endpoint under test:

POST /api/auth/register/
"""

import pytest
from rest_framework import status

REGISTER_URL = '/api/auth/register/'

VALID_REGISTRATION = {
    'username': 'newuser',
    'email': 'newuser@mail.com',
    'password': 'StrongPass123!',
    'confirm_password': 'StrongPass123!',
}



"""
Registration Tests
"""
@pytest.mark.django_db
class TestUserRegistration:

    def test_register_with_valid_data_returns_201(self, api_client):
        response = api_client.post(REGISTER_URL, VALID_REGISTRATION, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_register_creates_user_in_db(self, api_client):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        api_client.post(REGISTER_URL, VALID_REGISTRATION, format='json')
        assert User.objects.filter(username='newuser').exists()

    def test_register_duplicate_username_returns_400(self, api_client, user_factory):
        user_factory(username='newuser')
        response = api_client.post(REGISTER_URL, VALID_REGISTRATION, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch_returns_400(self, api_client):
        data = {**VALID_REGISTRATION, 'confirm_password': 'Different123!'}
        response = api_client.post(REGISTER_URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password_too_short_returns_400(self, api_client):
        data = {**VALID_REGISTRATION, 'password': 'weak', 'confirm_password': 'weak'}
        response = api_client.post(REGISTER_URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_numeric_only_password_returns_400(self, api_client):
        data = {**VALID_REGISTRATION, 'password': '9876543210', 'confirm_password': '9876543210'}
        response = api_client.post(REGISTER_URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data

    def test_register_missing_email_returns_400(self, api_client):
        data = {key: value for key, value in VALID_REGISTRATION.items() if key != 'email'}
        response = api_client.post(REGISTER_URL, data, format='json')    
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_missing_username_returns_400(self, api_client):
        data = {k: v for k, v in VALID_REGISTRATION.items() if k != 'username'}
        response = api_client.post(REGISTER_URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_blank_email_returns_400(self, api_client):
        data = {**VALID_REGISTRATION, 'email': ''}
        response = api_client.post(REGISTER_URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_not_in_response(self, api_client):
        response = api_client.post(REGISTER_URL, VALID_REGISTRATION, format='json')
        assert 'password' not in response.data

    def test_register_missin_password_returns_400(self, api_client):
        data = {'username': 'newuser', 'email': 'newuser@mail.com'}
        response = api_client.post(REGISTER_URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST