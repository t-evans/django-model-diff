Add "django_model_diff" to your INSTALLED_APPS setting.

Example usage:

```python
from django_model_diff.models import ComparableModelMixin
from django.db import models

class MyModel(ComparableModelMixin, models.Model):
    name = models.CharField()

foo_model = MyModel.objects.create(name='foo')
bar_model = MyModel.objects.create(name='bar')

differences_dict = foo_model.find_fields_with_differing_values(bar_model)
name_difference = differences_dict['name']
foo_value = name_difference[0]
bar_value = name_difference[1]
