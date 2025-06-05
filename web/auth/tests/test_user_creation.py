from unittest.mock import patch

from django.test import TestCase

from auth.serializers import UserCreationSerializer


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
