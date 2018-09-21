import graphene
from django_measurement.models import MeasurementField
from django_prices.models import MoneyField, TaxedMoneyField
from graphene_django.converter import convert_django_field
from graphene_django.fields import DjangoConnectionField

from graphene.relay import PageInfo
from graphql_relay.connection.arrayconnection import connection_from_list_slice

from .types.common import Weight
from .types.money import Money, TaxedMoney


@convert_django_field.register(TaxedMoneyField)
def convert_field_taxed_money(field, registry=None):
    return graphene.Field(TaxedMoney)


@convert_django_field.register(MoneyField)
def convert_field_money(field, registry=None):
    return graphene.Field(Money)


@convert_django_field.register(MeasurementField)
def convert_field_measurements(field, registry=None):
    return graphene.Field(Weight)


class PrefetchingConnectionField(DjangoConnectionField):

    @classmethod
    def resolve_connection(cls, connection, default_manager, args, iterable):
        if iterable is None:
            iterable = default_manager
        _len = iterable.count()
        connection = connection_from_list_slice(
            iterable,
            args,
            slice_start=0,
            list_length=_len,
            list_slice_length=_len,
            connection_type=connection,
            edge_type=connection.Edge,
            pageinfo_type=PageInfo,
        )
        connection.iterable = iterable
        connection.length = _len
        return connection
