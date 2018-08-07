def get_product_attributes_data(product):
    """Returns attributes associated with the product,
    as dict of ProductAttribute: AttributeChoiceValue values.
    """
    attributes = product.product_type.product_attributes.all()
    attributes_map = {
        attribute.pk: attribute.translated for attribute in attributes}
    values_map = get_attributes_display_map(product, attributes)
    return {
        attributes_map[attr_pk]: value_obj.translated
        for (attr_pk, value_obj) in values_map.items()}


def get_name_from_attributes(variant):
    """Generates ProductVariant's name based on its attributes."""
    attributes = variant.product.product_type.variant_attributes.all()
    values = get_attributes_display_map(variant, attributes)
    return generate_name_from_values(values)


def get_attributes_display_map(obj, attributes):
    """Returns attributes associated with an object,
    as dict of ProductAttribute: AttributeChoiceValue values.

    Args:
        attributes: ProductAttribute Iterable
    """
    display_map = {}
    for attribute in attributes:
        value = obj.attributes.get(str(attribute.pk))
        if value:
            choices = {str(a.pk): a.translated for a in attribute.values.all()}
            display_map[attribute.pk] = choices[value]
    return display_map


def generate_name_from_values(attributes_dict):
    """Generates name from AttributeChoiceValues. Attributes dict is sorted,
    as attributes order should be kept within each save.

    Args:
        attributes_dict: dict of attribute_pk: AttributeChoiceValue values
    """
    return ' / '.join(
        str(attributechoice_value)
        for attribute_pk, attributechoice_value in sorted(
            attributes_dict.items(),
            key=lambda x: x[0]))
