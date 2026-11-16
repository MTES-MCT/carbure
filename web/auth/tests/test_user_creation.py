from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from auth.serializers import UserCreationSerializer

User = get_user_model()


class UserCreationSerializerTest(TestCase):
    @patch("authtools.models.User.save")
    def test_desactivates_user_at_creation(self, user_save):
        data = {
            "name": "John Smith",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "newuser@example.com",
        }
        serializer = UserCreationSerializer(data=data)
        assert serializer.is_valid()

        user = serializer.save()
        assert not user.is_active

    def test_invalidates_user_when_passwords_mismatch(self):
        data = {
            "name": "John Smith",
            "password1": "strongpassword123",
            "password2": "STRONGPASSWORD789",
            "email": "newuser@example.com",
        }
        serializer = UserCreationSerializer(data=data)
        assert not serializer.is_valid()
        assert "password2" in serializer.errors
        assert serializer.errors["password2"][0] == "Les deux mots de passe ne correspondent pas."

    def test_invalidates_a_too_common_password(self):
        data = {
            "name": "John Smith",
            "password1": "password",
            "password2": "password",
            "email": "newuser@example.com",
        }
        serializer = UserCreationSerializer(data=data)
        assert not serializer.is_valid()
        assert "password2" in serializer.errors

    def test_invalidates_user_when_email_already_exists(self):
        User.objects.create(name="Some user", email="existing@example.com")
        data = {
            "name": "Some new user",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
            "email": "existing@example.com",
        }
        serializer = UserCreationSerializer(data=data)
        assert serializer.is_valid()
        validated_email = serializer.validated_data.get("email")
        assert validated_email == "existing@example.com"
