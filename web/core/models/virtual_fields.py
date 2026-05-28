class VirtualField(property):
    """Property-like descriptor with metadata, used as a virtual model field."""

    is_virtual_field = True

    def __init__(self, fget=None, fset=None, fdel=None, doc=None, *, verbose_name=None):
        super().__init__(fget, fset, fdel, doc)
        self.verbose_name = verbose_name


def virtual_field(*, verbose_name=None):
    """
    Decorator for declaring a model virtual field with metadata.

    Example:
        class MyModel(models.Model):
            amount = models.FloatField(default=0)
            rate = models.FloatField(default=0)

            @virtual_field(verbose_name="Computed total")
            def total(self):
                return self.amount * self.rate

    The decorated property remains non-persisted (not stored in DB),
    but can be discovered as a "virtual field" by exports/serializers.
    """

    def decorator(func):
        return VirtualField(func, verbose_name=verbose_name)

    return decorator
