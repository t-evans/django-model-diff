# User: troy
# Date: 3/19/14
#
# Copyright 2014, Nutrislice Inc.  All rights reserved.

from decimal import Decimal
from django.db.models.fields import NOT_PROVIDED


def has_non_whitespace_text(some_str):
    """
    Returns true if the provided string has non-whitespace characters.

    >>> has_non_whitespace_text("  ")
    False
    >>> has_non_whitespace_text("")
    False
    >>> has_non_whitespace_text(None)
    False
    >>> has_non_whitespace_text("Hello")
    True
    >>> has_non_whitespace_text("  Hello  ")
    True
    >>> has_non_whitespace_text(5)
    True
    """
    try:
        return some_str is not None and len(some_str.strip()) > 0
    except AttributeError:
        # If it's not a string, I guess we'll call that "non-whitespace"
        return True


class FieldAndValue(object):
    def __init__(self, obj, field):
        self.field = field
        self.value = getattr(obj, field.name)

    def get_default_model_value(self):
        default_value = None if self.field.default == NOT_PROVIDED else self.field.default
        return default_value

    def __unicode__(self):
        if self.value is not None:
            return unicode(self.value)
        else:
            return ""


def get_before_value(field_and_value, use_default_model_values_if_other_is_none):
    # Since "other" is None, the calling code may want to either return None for
    # all of the "other" objects fields, or it may want the default values for
    # each of those fields.
    if use_default_model_values_if_other_is_none:
        before_value = field_and_value.get_default_model_value()
    else:
        before_value = None
    return before_value


def get_field_value(obj, field, get_field_and_value):
    field_and_value = FieldAndValue(obj, field)
    if get_field_and_value:
        return field_and_value
    else:
        return field_and_value.value


class ComparableModelMixin(object):
    """
    Mixin to be used with django Model classes.  It provides methods for comparing the fields
    of one model to that of another and returning the differences.

    Currently, this assumes that floats that are extremely close are "equal" and it assumes
    that empty strings and null strings are "equal".
    """

    float_equality_tolerance = 1e-18
    empty_strings_are_equal_to_null_strings = True
    ignore_beginning_ending_whitespace_differences = True

    _latest_fields_with_differing_values = None

    def comparable_fields_to_ignore(self):
        """
        Contains a dictionary of values keyed by field name from the last time the _as_dict()
        method was called.  If fields change after the _as_dict() method is called, those changes
        will not be reflected here.
        """
        return ['Date Last Edited', 'Last Edited', 'date_last_edited', 'ID', 'uuid']

    def comparable_relationships_to_include(self):
        """
        By default, all relationships are excluded when comparing model objects.
        Its up to the implementing class to determine what it means for a
        relationship to be "equal" to another.
        """
        return []

    def _as_dict(self, get_field_and_value=False):
        latest_dict_values = dict([(f.verbose_name, get_field_value(self, f, get_field_and_value)) for f in self._meta.local_fields if not f.rel or f.name in self.comparable_relationships_to_include()])
        return latest_dict_values

    def _float_approx_equal(self, x, y):
        return abs(float(x) - float(y)) <= self.float_equality_tolerance

    def _approx_equal(self, x, y, *args, **kwargs):
        """
        Floats -----------------------------
        >>> comparable_model = ComparableModelMixin()
        >>> comparable_model._approx_equal(0.5, 0.50000000000000000001)
        True
        >>> comparable_model._approx_equal(0.5, 0.5000000000000001)
        False
        >>> comparable_model.float_equality_tolerance = 0.0001
        >>> comparable_model._approx_equal(0.5, 0.5000000000000001)
        True

        Strings -----------------------------
        >>> comparable_model._approx_equal(None, None)
        True
        >>> comparable_model._approx_equal(None, "")
        True
        >>> comparable_model._approx_equal("", "")
        True
        >>> comparable_model._approx_equal(None, " ")
        True
        >>> comparable_model._approx_equal("", " ")
        True
        >>> comparable_model._approx_equal("Bob", "John")
        False
        >>> comparable_model._approx_equal("John", "John ")
        True
        >>> comparable_model._approx_equal("John ", "John")
        True
        >>> comparable_model._approx_equal(5, "John")
        False

        >>> comparable_model.empty_strings_are_equal_to_null_strings = False
        >>> comparable_model._approx_equal(None, "")
        False
        >>> comparable_model._approx_equal(None, " ")
        False

        Integers -----------------------------
        >>> comparable_model._approx_equal(5, 6)
        False
        >>> comparable_model._approx_equal(5, 5)
        True
        >>> comparable_model._approx_equal(None, 5)
        False
        """
        if self.float_equality_tolerance is not None:
            typeX = type(x)
            typeY = type(y)
            if (typeX is float or typeX is Decimal) and (typeY is float or typeY is Decimal):
                return self._float_approx_equal(x, y)

        x_or_y_is_string = (isinstance(x, basestring) or isinstance(y, basestring))
        if self.empty_strings_are_equal_to_null_strings and x_or_y_is_string:
            try:
                if not has_non_whitespace_text(x) and not has_non_whitespace_text(y): # if they are both an empty or null string
                    return True
            except AttributeError: # Thrown if x or y is not a string
                return False

        # Todo: check a few more types.
        if self.ignore_beginning_ending_whitespace_differences and x_or_y_is_string:
            try:
                return x.strip() == y.strip()
            except AttributeError:
                return False
        else:
            return x == y

    def find_fields_with_differing_values(self, other, show_other_as_second_value=True, use_default_model_values_if_other_is_none=False):
        """
        Compares each of the fields of this object with 'other'.

        @param show_other_as_second_value: The values in the returned dictionary contain both of the model fields
            in an array of 2.  This indicates which order the values will appear in that array.
        @return: A dictionary containing the field differences found. The dictionary will be a list of tuplies
            containing the 2 differing values
        """
        def has_non_empty_value(value):
            if value is None:
                return False
            elif isinstance(value, list) and len(value) > 0:
                return True
            else:
                return not self._approx_equal(None, value)

        my_fields = self._as_dict()
        fields_to_ignore = self.comparable_fields_to_ignore()
        if other is not None:
            other_fields = other._as_dict()
            if show_other_as_second_value:
                self._latest_fields_with_differing_values = dict([(key, (value, other_fields.get(key))) for key, value in my_fields.iteritems() if not key in fields_to_ignore and not self._approx_equal(value, other_fields.get(key))])
            else:
                self._latest_fields_with_differing_values = dict([(key, (other_fields.get(key), value)) for key, value in my_fields.iteritems() if not key in fields_to_ignore and not self._approx_equal(value, other_fields.get(key))])
        else:
            if show_other_as_second_value:
                self._latest_fields_with_differing_values = dict([(key, (value, None)) for key, value in self._as_dict().iteritems() if not key in fields_to_ignore and has_non_empty_value(value)])
            else:
                # In this case, the "before" object is None
                my_fields = self._as_dict(True)
                self._latest_fields_with_differing_values = dict([(key, (get_before_value(field_and_value, use_default_model_values_if_other_is_none), field_and_value.value)) for key, field_and_value in my_fields.iteritems() if not key in fields_to_ignore and has_non_empty_value(field_and_value.value)])
                if use_default_model_values_if_other_is_none:
                    # Since the above may have added default values that match the new values, we need to
                    # check whether they are equal, and remove them if so (adding this logic into the
                    # one-liner, above, would be too ugly).
                    for key, before_and_after_values in self._latest_fields_with_differing_values.items():
                        if self._approx_equal(before_and_after_values[0], before_and_after_values[1]):
                            del self._latest_fields_with_differing_values[key]

        return self._latest_fields_with_differing_values

    def latest_fields_with_differing_values(self, other, show_other_as_second_value=True, use_default_model_values_if_other_is_none=False):
        """
        Efficiency method to use in place of find_fields_with_differing_values(). It will simply return the latest
        dictionary built by the other method (if any), or build one if needed. Don't use this if you need the
        updated differences.
        """
        if not self._latest_fields_with_differing_values:
            self.find_fields_with_differing_values(other, show_other_as_second_value=show_other_as_second_value, use_default_model_values_if_other_is_none=use_default_model_values_if_other_is_none)
        return self._latest_fields_with_differing_values

#    def relationships_with_differing_values(self, to_one_relationship_names=None, to_many_relationship_names=None):
#        pass