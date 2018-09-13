/* tslint:disable */
// This file was automatically generated and should not be edited.

// ====================================================
// GraphQL mutation operation: ProductImageReorder
// ====================================================

export interface ProductImageReorder_productImageReorder_errors {
  __typename: "Error";
  field: string | null;
  message: string | null;
}

export interface ProductImageReorder_productImageReorder_product_images_edges_node {
  __typename: "ProductImage";
  id: string;
  alt: string;
  sortOrder: number;
  url: string;
}

export interface ProductImageReorder_productImageReorder_product_images_edges {
  __typename: "ProductImageCountableEdge";
  node: ProductImageReorder_productImageReorder_product_images_edges_node;
}

export interface ProductImageReorder_productImageReorder_product_images {
  __typename: "ProductImageCountableConnection";
  edges: ProductImageReorder_productImageReorder_product_images_edges[];
}

export interface ProductImageReorder_productImageReorder_product {
  __typename: "Product";
  id: string;
  images: ProductImageReorder_productImageReorder_product_images | null;
}

export interface ProductImageReorder_productImageReorder {
  __typename: "ProductImageReorder";
  errors: (ProductImageReorder_productImageReorder_errors | null)[] | null;
  product: ProductImageReorder_productImageReorder_product | null;
}

export interface ProductImageReorder {
  productImageReorder: ProductImageReorder_productImageReorder | null;
}

export interface ProductImageReorderVariables {
  productId: string;
  imagesIds: (string | null)[];
}
