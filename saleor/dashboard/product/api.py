from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import renderers, status
from rest_framework.decorators import renderer_classes, api_view
from rest_framework.response import Response
from saleor.dashboard.views import staff_member_required

from rest_framework import serializers

from ...product.models import Product


class ReorderProductImagesSerializer(serializers.Serializer):
    order = serializers.ListField(child=serializers.IntegerField())


@staff_member_required
@api_view(['POST'])
@renderer_classes([renderers.JSONRenderer])
def reorder_product_images(request, product_pk):
    product = get_object_or_404(Product, pk=product_pk)
    serializer = ReorderProductImagesSerializer(data=request.data)
    if serializer.is_valid():
        for order, pk in enumerate(serializer.data['order']):
            try:
                img = product.images.get(pk=pk)
            except ObjectDoesNotExist:
                pass
            else:
                img.order = order
                img.save()
        return Response(status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
