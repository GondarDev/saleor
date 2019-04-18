import functools
import operator
from collections import defaultdict

import django_filters
from django.db.models import Q, Sum
from graphene_django.filter import GlobalIDFilter, GlobalIDMultipleChoiceFilter

from saleor.search.backends import picker

from ...product.models import Attribute, Product
from ..core.filters import EnumFilter, ListObjectTypeFilter, ObjectTypeFilter
from ..core.types.common import PriceRangeInput
from ..utils import get_nodes
from . import types
from .enums import StockAvailability
from .types.attributes import AttributeInput


def filter_products_by_attributes(qs, filter_value):
    attributes = Attribute.objects.prefetch_related('values')
    attributes_map = {
        attribute.slug: attribute.pk for attribute in attributes}
    values_map = {
        attr.slug: {value.slug: value.pk for value in attr.values.all()}
        for attr in attributes}
    queries = defaultdict(list)
    # Convert attribute:value pairs into a dictionary where
    # attributes are keys and values are grouped in lists
    for attr_name, val_slug in filter_value:
        if attr_name not in attributes_map:
            raise ValueError('Unknown attribute name: %r' % (attr_name, ))
        attr_pk = attributes_map[attr_name]
        attr_val_pk = values_map[attr_name].get(val_slug, val_slug)
        queries[attr_pk].append(attr_val_pk)
    # Combine filters of the same attribute with OR operator
    # and then combine full query with AND operator.
    combine_and = [
        functools.reduce(
            operator.or_, [
                Q(**{'variants__attributes__%s' % (key, ): v}) |
                Q(**{'attributes__%s' % (key, ): v}) for v in values])
        for key, values in queries.items()]
    query = functools.reduce(operator.and_, combine_and)
    return qs.filter(query).distinct()


def filter_products_by_price(qs, price_lte=None, price_gte=None):
    if price_lte:
        qs = qs.filter(price__lte=price_lte)
    if price_gte:
        qs = qs.filter(price__gte=price_gte)
    return qs


def filter_products_by_categories(qs, categories):
    categories = [
        category.get_descendants(include_self=True) for category in categories]
    ids = {category.id for tree in categories for category in tree}
    return qs.filter(category__in=ids)


def filter_products_by_collections(qs, collections):
    return qs.filter(collections__in=collections)


def sort_qs(qs, sort_by_product_order):
    if sort_by_product_order:
        qs = qs.order_by(sort_by_product_order['direction']
                         + sort_by_product_order['field'])
    return qs


def filter_products_by_stock_availability(qs, stock_availability):
    qs = qs.annotate(total_quantity=Sum('variants__quantity'))
    if stock_availability == StockAvailability.IN_STOCK:
        qs = qs.filter(total_quantity__gt=0)
    elif stock_availability == StockAvailability.OUT_OF_STOCK:
        qs = qs.filter(total_quantity__lte=0)
    return qs


def filter_attributes(qs, _, value):
    if value:
        value = [(v['slug'], v['attribute_value']) for v in value]
        qs = filter_products_by_attributes(qs, value)
    return qs


def filter_categories(qs, _, value):
    if value:
        categories = get_nodes(value, types.Category)
        qs = filter_products_by_categories(qs, categories)
    return qs


def filter_collections(qs, _, value):
    if value:
        collections = get_nodes(value, types.Collection)
        qs = filter_products_by_collections(qs, collections)
    return qs


def filter_price(qs, _, value):
    qs = filter_products_by_price(
        qs, price_lte=value.get('lte'), price_gte=value.get('gte'))
    return qs


def filter_stock_availability(qs, _, value):
    if value:
        qs = filter_products_by_stock_availability(qs, value)
    return qs


def filter_search(qs, _, value):
    if value:
        search = picker.pick_backend()
        qs &= search(value).distinct()
    return qs


class ProductFilter(django_filters.FilterSet):
    is_published = django_filters.BooleanFilter()
    collections = GlobalIDMultipleChoiceFilter(method=filter_collections)
    categories = GlobalIDMultipleChoiceFilter(method=filter_categories)
    price = ObjectTypeFilter(input_class=PriceRangeInput, method=filter_price)
    attributes = ListObjectTypeFilter(
        input_class=AttributeInput, method=filter_attributes)
    stock_availability = EnumFilter(
        input_class=StockAvailability, method=filter_stock_availability)
    product_type = GlobalIDFilter()
    search = django_filters.CharFilter(method=filter_search)

    class Meta:
        model = Product
        fields = [
            'is_published', 'collections', 'categories', 'price', 'attributes',
            'stock_availability', 'product_type', 'search'
        ]
