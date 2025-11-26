from typing import Tuple

from django.contrib.auth import get_user_model
from rest_framework.permissions import AND, OR
from rest_framework_api_key.models import APIKey

from core.models import UserRights, UserRightsRequests
from core.permissions import HasAdminRights, HasUserRights


# Patch is_verified() to always return True during tests
# This method is added by django_otp, we override it for tests
def _patch_is_verified():
    User = get_user_model()
    if not hasattr(User, "_is_verified_patched"):
        # Save the original method if it exists
        if hasattr(User, "is_verified"):
            User._is_verified_original = User.is_verified
        # Replace with a method that always returns True
        User.is_verified = lambda self: True
        User._is_verified_patched = True


# Apply the patch as soon as the module is imported
_patch_is_verified()


def setup_current_user(test, email, name, password, entity_rights=None, is_staff=False):
    if entity_rights is None:
        entity_rights = []
    User = get_user_model()
    user = User.objects.create_user(email=email, name=name, password=password, is_staff=is_staff)
    test.client.force_login(user)

    for entity, role in entity_rights:
        UserRights.objects.update_or_create(entity=entity, user=user, role=role)
        UserRightsRequests.objects.update_or_create(entity=entity, user=user, role=role)

    return user


def setup_current_user_with_jwt(test, email, name, password, entity_rights=None, is_staff=False):
    if entity_rights is None:
        entity_rights = []
    User = get_user_model()
    user = User.objects.create_user(email=email, name=name, password=password, is_staff=is_staff)

    for entity, role in entity_rights:
        UserRights.objects.update_or_create(entity=entity, user=user, role=role)
        UserRightsRequests.objects.update_or_create(entity=entity, user=user, role=role)

    # Create an ApiKey for the user and set it in the test client correctly.
    api_key, key = APIKey.objects.create_key(name="test")
    test.client.credentials(HTTP_X_API_KEY=key)
    # Authenticate (force jwt) the user in the test client
    test.client.force_authenticate(user=user)

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


class PermissionTestMixin:
    """
    Add this mixin to a test case to allow for quickly testing permissions for each viewset action.
    It first instanciates the viewset, and for each listed action, generates the matching permissions with get_permissions().
    Then it compares the result with the list of permissions defined in the test.

    Usage:

    from my_module.views.my_view import MyView

    class MyViewTest(TestCase, PermissionTestMixin):
        test_permissions():
            self.assertViewPermissions(
                MyView,
                [
                    (
                        # the first list contains view action names:
                        ["retrieve", "list"],
                        # the second list contains the associated permissions:
                        [HasUserRights([Entity.PRODUCER])]
                    ),
                    (
                        ["create", "update", "destroy"],
                        [HasUserRights([Entity.PRODUCER], [UserRights.RW, UserRights.ADMIN])]
                    ),
                    (
                        ["public_list"],
                        [IsAuthenticated()]
                    ),
                    (
                        ["admin_stuff"],
                        [HasAdminRights()]
                    )
                ]
            )
    """

    def assertViewPermissions(self, View, action_permissions: list[Tuple[list[str], list]]):
        view = View()

        # list all the actual actions and methods listed on the viewset so we can be sure we're testing the right things
        core_actions = ["list", "create", "retrieve", "update", "partial_update", "destroy"]
        view_core_actions = [a for a in core_actions if hasattr(view, a)]
        view_extra_actions = [a.__name__ for a in view.get_extra_actions()]
        view_methods = [
            name for name in dir(view) if callable(getattr(view, name, None)) and not name.startswith("__")
        ]  # list methods for when we use .as_view()
        view_actions = set(view_core_actions + view_extra_actions + view_methods)  # combine everything into a single set

        for actions, permissions in action_permissions:
            for action in actions:
                with self.subTest(f"action: {action}"):
                    self.assertIn(action, view_actions)
                    view.action = action
                    view_permissions = view.get_permissions()
                    self.assertPermissionsEqual(view_permissions, permissions)

                    # remove the current action for listed action sets
                    if action in view_core_actions:
                        view_core_actions.remove(action)
                    if action in view_extra_actions:
                        view_extra_actions.remove(action)

        # check if all actions were covered
        self.assertCountEqual(view_core_actions, [])
        self.assertCountEqual(view_extra_actions, [])

    def assertPermissionsEqual(self, first, second):
        if isinstance(first, list) and isinstance(second, list):
            self.assertEqual(len(first), len(second))
            for i in range(len(first)):
                self.assertPermissionsEqual(first[i], second[i])

        elif isinstance(first, (AND, OR)) and isinstance(second, type(first)):
            self.assertPermissionsEqual(first.op1, second.op1)
            self.assertPermissionsEqual(first.op2, second.op2)

        elif isinstance(first, HasUserRights) and isinstance(second, HasUserRights):
            self.assertCountEqual(first.entity_type or [], second.entity_type or [])
            self.assertCountEqual(first.role or [], second.role or [])

        elif isinstance(first, HasAdminRights) and isinstance(second, HasAdminRights):
            self.assertCountEqual(first.allow_external or [], second.allow_external or [])
            self.assertCountEqual(first.allow_role or [], second.allow_role or [])

        else:
            self.assertEqual(type(first), type(second))
