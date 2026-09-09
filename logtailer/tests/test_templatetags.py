from django.template import Context, Template
from django.test import TestCase

from logtailer.models import Filter
from logtailer.templatetags.logtailer_utils import filters_select


class FiltersSelectTagTest(TestCase):
    def test_returns_all_filters(self):
        error_filter = Filter.objects.create(name='errors', regex='ERROR.*')
        warning_filter = Filter.objects.create(name='warnings', regex='WARN.*')
        context = filters_select()
        self.assertCountEqual(
            context['filters'], [error_filter, warning_filter])

    def test_renders_select_with_filter_options(self):
        Filter.objects.create(name='errors', regex='ERROR.*')
        rendered = Template(
            '{% load logtailer_utils %}{% filters_select %}'
        ).render(Context())
        self.assertIn('id="filter-select"', rendered)
        self.assertIn('<option value="ERROR.*">errors</option>', rendered)
        self.assertIn('value="custom"', rendered)
