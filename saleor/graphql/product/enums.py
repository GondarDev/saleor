import graphene

from ...product import AttributeInputType
from ..core.enums import to_enum

AttributeInputTypeEnum = to_enum(AttributeInputType)


class AttributeTypeEnum(graphene.Enum):
    PRODUCT = "PRODUCT"
    VARIANT = "VARIANT"


class AttributeValueType(graphene.Enum):
    COLOR = "COLOR"
    GRADIENT = "GRADIENT"
    URL = "URL"
    STRING = "STRING"


class StockAvailability(graphene.Enum):
    IN_STOCK = "AVAILABLE"
    OUT_OF_STOCK = "OUT_OF_STOCK"


class CollectionPublished(graphene.Enum):
    PUBLISHED = "published"
    HIDDEN = "hidden"


class ProductTypeConfigurable(graphene.Enum):
    CONFIGURABLE = "configurable"
    SIMPLE = "simple"


class ProductTypeEnum(graphene.Enum):
    DIGITAL = "digital"
    SHIPPABLE = "shippable"


class AttributeSortField(graphene.Enum):
    NAME = "name"
    SLUG = "slug"
    VALUE_REQUIRED = "value_required"
    IS_VARIANT_ONLY = "is_variant_only"
    VISIBLE_IN_STOREFRONT = "visible_in_storefront"
    FILTERABLE_IN_STOREFRONT = "filterable_in_storefront"
    FILTERABLE_IN_DASHBOARD = "filterable_in_dashboard"

    DASHBOARD_VARIANT_POSITION = "dashboard_variant_position"
    DASHBOARD_PRODUCT_POSITION = "dashboard_product_position"
    STOREFRONT_SEARCH_POSITION = "storefront_search_position"
    AVAILABLE_IN_GRID = "available_in_grid"

    @property
    def description(self):
        if self == AttributeSortField.NAME:
            return "Sort attributes by name."
        if self == AttributeSortField.SLUG:
            return "Sort attributes by slug."
        if self == AttributeSortField.VALUE_REQUIRED:
            return "Sort attributes by the value required flag."
        if self == AttributeSortField.IS_VARIANT_ONLY:
            return "Sort attributes by the variant only flag."
        if self == AttributeSortField.VISIBLE_IN_STOREFRONT:
            return "Sort attributes by visibility in the storefront."
        if self == AttributeSortField.FILTERABLE_IN_STOREFRONT:
            return "Sort attributes by the filterable in storefront flag."
        if self == AttributeSortField.FILTERABLE_IN_DASHBOARD:
            return "Sort attributes by the filterable in dashboard flag."
        if self == AttributeSortField.DASHBOARD_VARIANT_POSITION:
            return "Sort variant attributes by their position in dashboard."
        if self == AttributeSortField.DASHBOARD_PRODUCT_POSITION:
            return "Sort product attributes by their position in dashboard."
        if self == AttributeSortField.STOREFRONT_SEARCH_POSITION:
            return "Sort attributes by their position in storefront."
        if self == AttributeSortField.AVAILABLE_IN_GRID:
            return (
                "Sort attributes based on whether they can be displayed "
                "or not in a product grid."
            )
        raise ValueError("Unsupported enum value: %s" % self.value)
