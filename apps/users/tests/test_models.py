"""
Test user model (Unit Testing)

Covers:
    - String representation(__str__)
    - User creation
    - Password hashing
    - Unique Username
    - Default Values
    - User deletion
"""


import pytest
from django.db import IntegrityError


@pytest.mark.django_db
class TestUserModel:

    def test_str_representation(self, user_factory):
        user = user_factory(username='anurodh')
        assert str(user) == 'anurodh'

    def test_user_creation(self, user_factory):
        user = user_factory(username='amrit', email='amrit@gmail.com')
        assert user.pk is not None
        assert user.username == 'amrit'
        assert user.email == 'amrit@gmail.com'

    def test_password_is_hashed(self, user_factory):
        user = user_factory(username='chandre', password='StrongPass123!')
        assert user.password != 'StrongPass123!'
        assert user.check_password('StrongPass123!')

    def test_username_is_unique(self, user_factory):
        user_factory(username='david')
        from django.contrib.auth import get_user_model
        User = get_user_model()
        with pytest.raises(IntegrityError):
            User.objects.create_user(username='david', email='david@mail.com')

    def test_default_values_for_user(self, user_factory):
        user = user_factory()
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'

    def test_user_deletion(self, user_factory):
        user = user_factory(username='ram', email='ram@gmail.com')
        assert user.delete() == (1, {'users.User': 1})