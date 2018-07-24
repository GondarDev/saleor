import decimal

import graphene
from django_prices.templatetags import prices_i18n
from django_prices_vatlayer import models as vatlayer_models
from graphene.types import Scalar
from graphene_django import DjangoObjectType
from graphql.language import ast

from .connection import CountableConnection


# FIXME: not yet merged https://github.com/graphql-python/graphene/pull/726
class Decimal(Scalar):
    """The `Decimal` scalar type represents a python Decimal."""

    @staticmethod
    def serialize(dec):
        assert isinstance(dec, decimal.Decimal), (
            'Received not compatible Decimal "{}"'.format(repr(dec)))
        return str(dec)

    @staticmethod
    def parse_value(value):
        return decimal.Decimal(value)

    @classmethod
    def parse_literal(cls, node):
        if isinstance(node, ast.StringValue):
            return cls.parse_value(node.value)


class CountryDisplay(graphene.ObjectType):
    code = graphene.String(description='Country code.', required=True)
    country = graphene.String(description='Country.', required=True)


class CountableDjangoObjectType(DjangoObjectType):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, *args, **kwargs):
        # Force it to use the countable connection
        countable_conn = CountableConnection.create_type(
            "{}CountableConnection".format(cls.__name__),
            node=cls)
        super().__init_subclass_with_meta__(
            *args, connection=countable_conn, **kwargs)


class Error(graphene.ObjectType):
    field = graphene.String(
        description="""Name of a field that caused the error. A value of
        `null` indicates that the error isn't associated with a particular
        field.""", required=False)
    message = graphene.String(description='The error message.')

    class Meta:
        description = 'Represents an error in the input of a mutation.'


class LanguageDisplay(graphene.ObjectType):
    code = graphene.String(description='Language code.', required=True)
    language = graphene.String(description='Language.', required=True)


class Money(graphene.ObjectType):
    currency = graphene.String(description='Currency code.', required=True)
    amount = graphene.Float(description='Amount of money.', required=True)
    localized = graphene.String(
        description='Money formatted according to the current locale.',
        required=True)

    class Meta:
        description = 'Represents amount of money in specific currency.'

    def resolve_localized(self, info):
        return prices_i18n.amount(self)


class MoneyRange(graphene.ObjectType):
    start = graphene.Field(
        Money, description='Lower bound of a price range.')
    stop = graphene.Field(
        Money, description='Upper bound of a price range.')

    class Meta:
        description = 'Represents a range of amounts of money.'


class PermissionDisplay(graphene.ObjectType):
    code = graphene.String(
        description='Internal code for permission.', required=True)
    name = graphene.String(
        description='Describe action(s) allowed to do by permission.',
        required=True)

    class Meta:
        description = 'Represents a permission object in a friendly form.'


class SeoInput(graphene.InputObjectType):
    title = graphene.String(description='SEO title.')
    description = graphene.String(description='SEO description.')


class TaxedMoney(graphene.ObjectType):
    currency = graphene.String(description='Currency code.', required=True)
    gross = graphene.Field(
        Money, description='Amount of money including taxes.', required=True)
    net = graphene.Field(
        Money, description='Amount of money without taxes.', required=True)
    tax = graphene.Field(Money, description='Amount of taxes.', required=True)

    class Meta:
        description = """Represents a monetary value with taxes. In
        case when taxes were not applied, net and gross values will be equal.
        """


class TaxedMoneyRange(graphene.ObjectType):
    start = graphene.Field(
        TaxedMoney, description='Lower bound of a price range.')
    stop = graphene.Field(
        TaxedMoney, description='Upper bound of a price range.')

    class Meta:
        description = 'Represents a range of monetary values.'


class Shop(graphene.ObjectType):
    countries = graphene.List(
        CountryDisplay, description='List of countries available in the shop.',
        required=True)
    currencies = graphene.List(
        graphene.String, description='List of available currencies.',
        required=True)
    default_currency = graphene.String(
        description='Default shop\'s currency.', required=True)
    domain = graphene.Field(
        lambda: Domain, required=True, description='Shop\'s domain data.')
    languages = graphene.List(
        LanguageDisplay,
        description='List of the shops\'s supported languages.', required=True)
    name = graphene.String(description='Shop\'s name.', required=True)
    permissions = graphene.List(
        PermissionDisplay, description='List of available permissions.',
        required=True)
    phone_prefixes = graphene.List(
        graphene.String, description='List of possible phone prefixes.',
        required=True)
    tax_rates = graphene.List(
        lambda: VAT, description='List of VAT tax rates configured in the shop.',
        required=True)
    tax_rate = graphene.Field(
        lambda: VAT, description='VAT tax rates for a specific country.',
        required=False, country_code=graphene.Argument(graphene.String))

    class Meta:
        description = '''
        Represents a shop resource containing general shop\'s data
        and configuration.'''

    def resolve_tax_rates(self, info):
        return vatlayer_models.VAT.objects.order_by('country_code')

    def resolve_tax_rate(self, info, country_code):
        return vatlayer_models.VAT.objects.filter(
            country_code=country_code).first()


class Domain(graphene.ObjectType):
    host = graphene.String(
        description='The host name of the domain.', required=True)
    ssl_enabled = graphene.Boolean(
        description='Inform if SSL is enabled.', required=True)
    url = graphene.String(
        description='Shop\'s absolute URL.', required=True)

    class Meta:
        description = 'Represents shop\'s domain.'


class VAT(graphene.ObjectType):
    country_code = graphene.String(description='Country code.', required=True)
    standard_rate = graphene.Float(
        description='Standard VAT rate in percent.')
    reduced_rates = graphene.List(
        lambda: ReducedRate,
        description='Country\'s VAT rate exceptions for specific types of goods.')

    class Meta:
        description = 'Represents a VAT rate for a country.'

    def resolve_standard_rate(self, info):
        return self.data.get('standard_rate')

    def resolve_reduced_rates(self, info):
        reduced_rates = self.data.get('reduced_rates', {}) or {}
        return [
            ReducedRate(rate=rate, type=type)
            for type, rate in reduced_rates.items()]


class ReducedRate(graphene.ObjectType):
    rate = graphene.Float(
        description='Reduced VAT rate in percent.', required=True)
    type = graphene.String(description='A type of goods.', required=True)

    class Meta:
        description = 'Represents a reduced VAT rate for a particular type of goods.'
