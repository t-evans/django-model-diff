# User: troy
# Date: 3/19/14
#
# Copyright 2014, Nutrislice Inc.  All rights reserved.
from decimal import Decimal
from unittest import TestCase
from django_model_diff.models import ComparableModelMixin


class ComparableModelMixinTest(TestCase):
    def test_float_approx_equal(self):
        mixin = ComparableModelMixin()
        self.assertTrue(mixin._float_approx_equal(0.5, Decimal(0.5000000)))
