from enum import Enum


class OrderErrorCode(Enum):
    CANNOT_CANCEL_FULFILLMENT = "cannot_cancel_fulfillment"
    CANNOT_CANCEL_ORDER = "cannot_cancel_order"
    CANNOT_DELETE = "cannot_delete"
    CANNOT_REFUND = "cannot_refund"
    CAPTURE_INACTIVE_PAYMENT = "capture_inactive_payment"
    NOT_EDITABLE = "not_editable"
    FULFILL_ORDER_LINE = "fulfill_order_line"
    GRAPHQL_ERROR = "graphql_error"
    INVALID = "invalid"
    NOT_FOUND = "not_found"
    ORDER_INVALID_SHIPPING_METHOD = "order_invalid_shipping_method"
    ORDER_NO_SHIPPING_ADDRESS = "order_no_shipping_address"
    PAYMENT_ERROR = "payment_error"
    PAYMENT_MISSING = "payment_missing"
    REQUIRED = "required"
    SHIPPING_METHOD_REQUIRED = "shipping_method_required"
    UNIQUE = "unique"
    VOID_INACTIVE_PAYMENT = "void_inactive_payment"
    ZERO_QUANTITY = "zero_quantity"
