import datetime

from mock import Mock

from saleor.product import models
from saleor.product.models import Product
from saleor.product.models import ProductClass
from saleor.product.models import ProductVariant
from saleor.product.utils import get_availability, filter_by_attribute


def test_stock_selector(product_in_stock):
    variant = product_in_stock.variants.get()
    preferred_stock = variant.select_stockrecord(5)
    assert preferred_stock.quantity_available >= 5


def test_stock_allocator(product_in_stock):
    variant = product_in_stock.variants.get()
    stock = variant.select_stockrecord(5)
    assert stock.quantity_allocated == 0
    models.Stock.objects.allocate_stock(stock, 1)
    stock = models.Stock.objects.get(pk=stock.pk)
    assert stock.quantity_allocated == 1


def test_product_page_redirects_to_correct_slug(client, product_in_stock):
    uri = product_in_stock.get_absolute_url()
    uri = uri.replace(product_in_stock.get_slug(), 'spanish-inquisition')
    response = client.get(uri)
    assert response.status_code == 301
    location = response['location']
    if location.startswith('http'):
        location = location.split('http://testserver')[1]
    assert location == product_in_stock.get_absolute_url()


def test_product_preview(admin_client, client, product_in_stock):
    product_in_stock.available_on = (
        datetime.date.today() + datetime.timedelta(days=7))
    product_in_stock.save()
    response = client.get(product_in_stock.get_absolute_url())
    assert response.status_code == 404
    response = admin_client.get(product_in_stock.get_absolute_url())
    assert response.status_code == 200


def test_availability(product_in_stock, monkeypatch, settings):
    availability = get_availability(product_in_stock)
    assert availability.price_range == product_in_stock.get_price_range()
    assert availability.price_range_local_currency is None
    monkeypatch.setattr(
        'django_prices_openexchangerates.models.get_rates',
        lambda c: {'PLN': Mock(rate=2)})
    settings.DEFAULT_CURRENCY = 'USD'
    settings.DEFAULT_COUNTRY = 'PL'
    settings.OPENEXCHANGERATES_API_KEY = 'fake-key'
    availability = get_availability(product_in_stock, local_currency='PLN')
    assert availability.price_range_local_currency.min_price.currency == 'PLN'
    assert availability.available


def test_filtering_by_attribute(db, color_attribute):
    product_class_a = ProductClass.objects.create(
        name='New class', has_variants=True)
    product_class_a.product_attributes.add(color_attribute)
    product_class_b = ProductClass.objects.create(name='New class',
                                                  has_variants=True)
    product_class_b.variant_attributes.add(color_attribute)
    product_a = Product.objects.create(
        name='Test product a', price=10, weight=1,
        product_class=product_class_a)
    variant_a = ProductVariant.objects.create(product=product_a, sku='1234')
    product_b = Product.objects.create(
        name='Test product b', price=10, weight=1,
        product_class=product_class_b)
    variant_b = ProductVariant.objects.create(product=product_b, sku='12345')
    color = color_attribute.values.first()
    color_2 = color_attribute.values.last()
    product_a.set_attribute(color_attribute.pk, color.pk)
    product_a.save()
    variant_b.set_attribute(color_attribute.pk, color.pk)
    variant_b.save()

    filtered = filter_by_attribute(Product.objects.all(), color_attribute,
                                   color)
    assert product_a in filtered
    assert product_b in filtered

    product_a.set_attribute(color_attribute.pk, color_2.pk)
    product_a.save()
    filtered = filter_by_attribute(Product.objects.all(), color_attribute,
                                   color)
    assert product_a not in filtered
    assert product_b in filtered
    filtered = filter_by_attribute(Product.objects.all(), color_attribute,
                                   color_2)
    assert product_a in filtered
    assert product_b not in filtered
