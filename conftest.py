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





"""
CONSTANTS
"""