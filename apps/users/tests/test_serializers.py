"""
Unit tests for User Register Serializer

Covers:
    - Valid data is serializable
    - Password mismatch raises error
    - Weak password
    - Missing email
    - Password is write_only
"""

from users.serializers.register_serializer import UserRegisterSerializer


class TestUserRegisterSerializer:

    def test_valid_data_is_serializable(self, db):
        data = {
            'username': 'anu',
            'email': 'anu@mail.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        }
        serializer = UserRegisterSerializer(data=data)
        assert serializer.is_valid(), serializer.errors

    def test_password_mismatch_raises_error(self, db):
        data = {
            'username': 'anu',
            'email': 'anu@mail.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123',
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'confirm_password' in serializer.errors

    def test_weak_password_fails_validation(self, db):
        data = {
            'username': 'anu',
            'email': 'anu@mail.com',
            'password': 'weak',
            'confirm_password': 'weak',
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_missing_email(self, db):
        data = {
            'username': 'anu',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        }
        serializer = UserRegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_password_is_write_only(self, db):
        data = {
            'username': 'anu',
            'email': 'anu@mail.com',
            'password': 'StrongPass123!',
            'confirm_password': 'StrongPass123!',
        }
        serializer = UserRegisterSerializer(data=data)
        assert serializer.is_valid()
        serializer.save()
        assert 'password' not in serializer.data
        assert 'confirm_password' not in serializer.data