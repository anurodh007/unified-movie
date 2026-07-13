"""
Tests user permissions

Endpoints under test:

GET /api/users/<str:username>/
PUT /api/users/<str:username>/
PATCH /api/users/<str:username>/
"""

import pytest
from django.urls import reverse
from rest_framework import status



"""
User Permission Tests
"""
@pytest.mark.django_db
class TestUserPermission:

    def test_authenticated_user_can_view_own_profile(self, auth_client, user):
        url = reverse('user_detail', kwargs={'username': user.username})
        response = auth_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_authenticated_user_can_update_own_profile(self, auth_client, user):
        url = reverse('user_detail', kwargs={'username': user.username})
        response = auth_client.patch(url, {'first_name': 'Test'}, format='json')
        assert response.status_code == status.HTTP_200_OK

    def test_user_cannot_update_other_user_profile(self, auth_client, other_user):
        url = reverse('user_detail', kwargs={'username': other_user.username})
        response = auth_client.patch(url, {'first_name': 'Hello', 'last_name': 'World'}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_anonymous_user_cannot_update_profile(self, api_client, user):
        url = reverse('user_detail', kwargs={'username': user.username})
        response = api_client.patch(url, {'bio': 'Hello. I am unknown'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_can_view_other_user_profile(self, api_client, other_user):
        url = reverse('user_detail', kwargs={'username': other_user.username})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK