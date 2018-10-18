/* tslint:disable */
// This file was automatically generated and should not be edited.

// ====================================================
// GraphQL query operation: RootCategories
// ====================================================

export interface RootCategories_categories_edges_node_children {
  __typename: "CategoryCountableConnection";
  totalCount: number | null;
}

export interface RootCategories_categories_edges_node_products {
  __typename: "ProductCountableConnection";
  totalCount: number | null;
}

export interface RootCategories_categories_edges_node {
  __typename: "Category";
  id: string;
  name: string;
  children: RootCategories_categories_edges_node_children | null;
  products: RootCategories_categories_edges_node_products | null;
}

export interface RootCategories_categories_edges {
  __typename: "CategoryCountableEdge";
  node: RootCategories_categories_edges_node;
}

export interface RootCategories_categories {
  __typename: "CategoryCountableConnection";
  edges: RootCategories_categories_edges[];
}

export interface RootCategories {
  categories: RootCategories_categories | null;
}
