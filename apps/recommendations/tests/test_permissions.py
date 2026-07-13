"""
Test Recommendation permissions

Endpoint under test:

GET /api/recommendations/
"""

import pytest
from django.urls import reverse
from rest_framework import status



"""
Recommendation Permission Test
"""
@pytest.mark.django_db
class TestRecommendationPermission:

    def test_anonymous_user_cannot_access_recommendations(self, api_client):
        response = api_client.get(reverse('movie-recommendations'))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_authenticated_user_can_access_recommendations(self, auth_client):
        response = auth_client.get(reverse('movie-recommendations'))
        assert response.status_code == status.HTTP_200_OK