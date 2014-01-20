from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import (ProductImage, BagVariant, Bag, ShirtVariant, Shirt,
                     Category, FixedProductDiscount)


class ImageAdminInline(admin.StackedInline):

    model = ProductImage


class BagVariantInline(admin.StackedInline):

    model = BagVariant


class BagAdmin(admin.ModelAdmin):

    inlines = [BagVariantInline, ImageAdminInline]


class ShirtVariant(admin.StackedInline):

    model = ShirtVariant


class ShirtAdmin(admin.ModelAdmin):

    inlines = [ShirtVariant, ImageAdminInline]


admin.site.register(Bag, BagAdmin)
admin.site.register(Shirt, ShirtAdmin)
admin.site.register(Category, MPTTModelAdmin)
admin.site.register(FixedProductDiscount)
