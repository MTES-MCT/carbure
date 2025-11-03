class ListWithObjectPermissionsMixin:
    """
    Mixin for list() actions that need to check object-level permissions.

    Override get_permission_object() to specify which object to check permissions on.
    By default, checks permissions on the first object in the filtered queryset.
    """

    def get_permission_object(self, first_obj):
        """
        Override this method to return the object to check permissions on.

        Args:
            first_obj: The first object from the filtered queryset (or None if empty)

        Returns:
            The object to check permissions on (can be first_obj itself or a related object)
        """
        return first_obj

    def list(self, request, *args, **kwargs):
        """List objects with object-level permission check on the first result."""
        queryset = self.filter_queryset(self.get_queryset())
        first_obj = queryset.first()
        permission_obj = self.get_permission_object(first_obj)

        if permission_obj is not None:
            self.check_object_permissions(request, permission_obj)

        return super().list(request, *args, **kwargs)
