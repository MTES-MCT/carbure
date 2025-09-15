from django.contrib.auth import get_user_model
from django.urls import reverse
from django_otp.plugins.otp_email.models import EmailDevice

from core.models import UserRights, UserRightsRequests


def setup_current_user(test, email, name, password, entity_rights=None, is_staff=False):
    if entity_rights is None:
        entity_rights = []
    User = get_user_model()
    user = User.objects.create_user(email=email, name=name, password=password, is_staff=is_staff)
    loggedin = test.client.login(username=user.email, password=password)
    assert loggedin

    for entity, role in entity_rights:
        UserRights.objects.update_or_create(entity=entity, user=user, role=role)
        UserRightsRequests.objects.update_or_create(entity=entity, user=user, role=role)

    response = test.client.get(reverse("auth-request-otp"))
    assert response.status_code == 200
    device, _ = EmailDevice.objects.get_or_create(user=user)
    response = test.client.post(reverse("auth-verify-otp"), {"otp_token": device.token})
    assert response.status_code == 200

    return user


# def assert_roles_have_permission(test,user, entity, roles, http_callback):
#     for role in roles:
#         UserRights.objects.update(entity=entity, user=user, role=role)
#         response = http_callback()
#         test.assertEqual(response.status_code, status.HTTP_200_OK)


def assert_object_contains_data(test, obj, data, object_name="objet"):
    for field_name, expected_value in data.items():
        if isinstance(obj, dict):
            actual_value = obj.get(field_name)
        else:
            actual_value = getattr(obj, field_name)
        test.assertEqual(
            actual_value,
            expected_value,
            f"Le champ '{field_name}' de {object_name} ne correspond pas. Attendu: {expected_value}, Obtenu: {actual_value}",
        )


# Take a viewset and an endpoint and return the permissions for that endpoint


def get_viewset_permissions(viewset, endpoint):
    initialized_viewset = viewset()
    initialized_viewset.action = endpoint
    permissions = initialized_viewset.get_permissions()
    return permissions


"""
    Get the first permission of a specific endpoint from a viewset.

    Args:
        viewset: The viewset class to test
        endpoint: The name of the action/endpoint to test

    Returns:
        The first permission configured for this endpoint

    Example:
        class MyViewsetPermissionsTests(TestCase):
            def setUp(self):
                self.viewset = MyViewset()
                self.read_write_endpoints = [
                    "endpoint1",
                    "endpoint2",
                ]
                self.read_only_endpoints = ["retrieve"]

            def test_permissions_read_write_for_endpoints(self):
                for endpoint in self.read_write_endpoints:
                    permission = get_first_viewset_permission(MyViewset, endpoint)
                    self.assertEqual(permission.role, [UserRights.ADMIN, UserRights.RW])
                    self.assertEqual(permission.entity_type, [Entity.BIOMETHANE_PRODUCER])

            def test_permissions_read_only_for_endpoints(self):
                for endpoint in self.read_only_endpoints:
                    permission = get_first_viewset_permission(MyViewset, endpoint)
                    self.assertEqual(permission.role, None)
                    self.assertEqual(permission.entity_type, [Entity.BIOMETHANE_PRODUCER])
    """


def get_first_viewset_permission(viewset, endpoint):
    permissions = get_viewset_permissions(viewset, endpoint)
    assert len(permissions) > 0

    return permissions[0]
