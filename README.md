Add "django_model_diff" to your INSTALLED_APPS setting.

Example usage:

from django_model_diff.models import ComparableModelMixin
from django.db import models


class MyModel(ComparableModelMixin, models.Model):
    name = models.CharField()


foo_model = MyModel.objects.create(name='foo')
bar_model = MyModel.objects.create(name='bar')

foo_model.find_fields_with_differing_values(bar_model)
