from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.tax_list, name='taxes'),
    url(r'^(?P<country_code>[A-Z]{2})/details/$', views.tax_details,
        name='tax-details'),
]
