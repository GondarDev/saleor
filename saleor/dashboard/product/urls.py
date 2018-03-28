from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.product_list, name='product-list'),
    url(r'^(?P<pk>[0-9]+)/$',
        views.product_detail, name='product-detail'),
    url(r'^(?P<pk>[0-9]+)/publish/$', views.product_toggle_is_published,
        name='product-publish'),
    url(r'^(?P<pk>[0-9]+)/update/$',
        views.product_edit, name='product-update'),
    url(r'^(?P<pk>[0-9]+)/delete/$',
        views.product_delete, name='product-delete'),
    url(r'^add/(?P<type_pk>[0-9]+)/$',
        views.product_create, name='product-add'),
    url(r'^bulk-update/$',
        views.product_bulk_update, name='product-bulk-update'),
    url(r'^add/select-type/$',
        views.product_select_type, name='product-add-select-type'),

    url(r'^types/$',
        views.product_type_list, name='product-type-list'),
    url(r'^types/add/$',
        views.product_type_create, name='product-type-add'),
    url(r'^types/(?P<pk>[0-9]+)/update/$',
        views.product_type_edit, name='product-type-update'),
    url(r'^types/(?P<pk>[0-9]+)/delete/$',
        views.product_type_delete, name='product-type-delete'),

    url(r'^(?P<product_pk>[0-9]+)/variants/add/$',
        views.variant_add, name='variant-add'),
    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/$',
        views.variant_details, name='variant-details'),
    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/update/$',
        views.variant_edit, name='variant-update'),
    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/delete/$',
        views.variant_delete, name='variant-delete'),
    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/images/$',
        views.variant_images, name='variant-images'),

    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/stock/add/$',
        views.stock_add, name='variant-stock-add'),
    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/stock/'
        r'(?P<stock_pk>[0-9]+)/$',
        views.stock_details, name='variant-stock-details'),
    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/stock/'
        r'(?P<stock_pk>[0-9]+)/update/$',
        views.stock_edit, name='variant-stock-update'),
    url(r'^(?P<product_pk>[0-9]+)/variants/(?P<variant_pk>[0-9]+)/stock/'
        r'(?P<stock_pk>[0-9]+)/delete/$',
        views.stock_delete, name='variant-stock-delete'),

    url(r'^(?P<product_pk>[0-9]+)/images/$', views.product_images,
        name='product-image-list'),
    url(r'^(?P<product_pk>[0-9]+)/images/add/$',
        views.product_image_add, name='product-image-add'),
    url(r'^(?P<product_pk>[0-9]+)/images/(?P<img_pk>[0-9]+)/$',
        views.product_image_edit, name='product-image-update'),
    url(r'^(?P<product_pk>[0-9]+)/images/(?P<img_pk>[0-9]+)/delete/$',
        views.product_image_delete, name='product-image-delete'),

    url(r'^(?P<product_pk>[0-9]+)/images/reorder/$',
        views.ajax_reorder_product_images, name='product-images-reorder'),
    url(r'^(?P<product_pk>[0-9]+)/images/upload/$',
        views.ajax_upload_image, name='product-images-upload'),

    url(r'attributes/$',
        views.attribute_list, name='product-attributes'),
    url(r'attributes/(?P<pk>[0-9]+)/$',
        views.attribute_detail, name='product-attribute-detail'),
    url(r'attributes/add/$',
        views.attribute_add, name='product-attribute-add'),
    url(r'attributes/(?P<pk>[0-9]+)/update/$',
        views.attribute_edit, name='product-attribute-update'),
    url(r'attributes/(?P<pk>[0-9]+)/delete/$',
        views.attribute_delete, name='product-attribute-delete'),
    url(r'attributes/(?P<attribute_pk>[0-9]+)/value/add/$',
        views.attribute_choice_value_add,
        name='product-attribute-value-add'),
    url(r'attributes/(?P<attribute_pk>[0-9]+)/value/(?P<value_pk>[0-9]+)/update/$',  # noqa
        views.attribute_choice_value_edit,
        name='product-attribute-value-update'),
    url(r'attributes/(?P<attribute_pk>[0-9]+)/value/(?P<value_pk>[0-9]+)/delete/$',  # noqa
        views.attribute_choice_value_delete,
        name='product-attribute-value-delete'),

    url(r'^ajax/variants/$',
        views.ajax_available_variants_list, name='ajax-available-variants'),
    url(r'^ajax/products/$',
        views.ajax_products_list, name='ajax-products')]
