import random

import factory


class RandomInstanceOf(factory.declarations.BaseDeclaration):
    def __init__(self, model, **kwargs):
        self.model = model
        super().__init__(**kwargs)

    def evaluate(self, instance, step, extra):
        count = self.model.objects.count()
        index = random.randint(0, count - 1)
        return self.model.objects.all()[index]
