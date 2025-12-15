import random

import factory


class RandomInstanceOf(factory.declarations.BaseDeclaration):
    def __init__(self, model, fallback_factory=None, **kwargs):
        self.model = model
        self.fallback_factory = fallback_factory
        super().__init__(**kwargs)

    def evaluate(self, instance, step, extra):
        count = self.model.objects.count()
        if count == 0:
            if self.fallback_factory is not None:
                return self.fallback_factory()
            else:
                return None
        index = random.randint(0, count - 1)
        return self.model.objects.all()[index]
