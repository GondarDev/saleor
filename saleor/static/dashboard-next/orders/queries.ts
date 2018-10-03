import gql from "graphql-tag";

import { TypedQuery } from "../queries";
import { OrderDetails, OrderDetailsVariables } from "./types/OrderDetails";
import { OrderList, OrderListVariables } from "./types/OrderList";
import {
  OrderVariantSearch,
  OrderVariantSearchVariables
} from "./types/OrderVariantSearch";

export const fragmentOrderEvent = gql`
  fragment OrderEventFragment on OrderEvent {
    id
    amount
    date
    email
    emailType
    message
    quantity
    type
    user {
      email
    }
  }
`;
export const fragmentAddress = gql`
  fragment AddressFragment on Address {
    city
    cityArea
    companyName
    country {
      __typename
      code
      country
    }
    countryArea
    firstName
    id
    lastName
    phone
    postalCode
    streetAddress1
    streetAddress2
  }
`;
export const fragmentOrderLine = gql`
  fragment OrderLineFragment on OrderLine {
    id
    productName
    productSku
    quantity
    quantityFulfilled
    unitPrice {
      gross {
        amount
        currency
      }
      net {
        amount
        currency
      }
    }
    thumbnailUrl
  }
`;

export const fragmentOrderDetails = gql`
  ${fragmentAddress}
  ${fragmentOrderEvent}
  ${fragmentOrderLine}
  fragment OrderDetailsFragment on Order {
    id
    billingAddress {
      ...AddressFragment
    }
    created
    events {
      ...OrderEventFragment
    }
    fulfillments {
      id
      lines {
        edges {
          node {
            id
            quantity
            orderLine {
              ...OrderLineFragment
            }
          }
        }
      }
      fulfillmentOrder
      status
      trackingNumber
    }
    lines {
      edges {
        node {
          ...OrderLineFragment
        }
      }
      thumbnailUrl
    }
    number
    paymentStatus
    shippingAddress {
      ...AddressFragment
    }
    shippingMethod {
      id
    }
    shippingMethodName
    shippingPrice {
      gross {
        amount
        currency
      }
    }
    status
    subtotal {
      gross {
        amount
        currency
      }
    }
    total {
      gross {
        amount
        currency
      }
      tax {
        amount
        currency
      }
    }
    totalAuthorized {
      amount
      currency
    }
    totalCaptured {
      amount
      currency
    }
    user {
      id
      email
    }
    userEmail
    availableShippingMethods {
      id
      name
    }
  }
`;

export const orderListQuery = gql`
  ${fragmentAddress}
  query OrderList($first: Int, $after: String, $last: Int, $before: String) {
    orders(before: $before, after: $after, first: $first, last: $last) {
      edges {
        node {
          __typename
          billingAddress {
            ...AddressFragment
          }
          created
          id
          number
          paymentStatus
          status
          total {
            __typename
            gross {
              __typename
              amount
              currency
            }
          }
          userEmail
        }
      }
      pageInfo {
        hasPreviousPage
        hasNextPage
        startCursor
        endCursor
      }
    }
  }
`;
export const TypedOrderListQuery = TypedQuery<OrderList, OrderListVariables>(
  orderListQuery
);

export const orderDetailsQuery = gql`
  ${fragmentOrderDetails}
  query OrderDetails($id: ID!) {
    order(id: $id) {
      ...OrderDetailsFragment
    }
    shop {
      countries {
        code
        country
      }
    }
  }
`;
export const TypedOrderDetailsQuery = TypedQuery<
  OrderDetails,
  OrderDetailsVariables
>(orderDetailsQuery);

export const orderVariantSearchQuery = gql`
  query OrderVariantSearch($search: String!) {
    products(query: $search, first: 20) {
      edges {
        node {
          id
          name
          variants {
            edges {
              node {
                id
                name
                sku
                stockQuantity
              }
            }
          }
        }
      }
    }
  }
`;
export const TypedOrderVariantSearch = TypedQuery<
  OrderVariantSearch,
  OrderVariantSearchVariables
>(orderVariantSearchQuery);
