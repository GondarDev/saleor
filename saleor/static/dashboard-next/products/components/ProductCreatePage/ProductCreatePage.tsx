import { withStyles } from "@material-ui/core/styles";
import * as React from "react";

import { AttributeType } from "../../";
import { UserError } from "../../../";
import Container from "../../../components/Container";
import Form from "../../../components/Form";
import PageHeader from "../../../components/PageHeader";
import SaveButtonBar, {
  SaveButtonBarState
} from "../../../components/SaveButtonBar/SaveButtonBar";
import SeoForm from "../../../components/SeoForm";
import i18n from "../../../i18n";
import ProductAvailabilityForm from "../ProductAvailabilityForm";
import ProductDetailsForm from "../ProductDetailsForm";
import ProductOrganization from "../ProductOrganization";
import ProductPricing from "../ProductPricing";

interface FormData {
  attributes: Array<{
    slug: string;
    value: string;
  }>;
  available: boolean;
  availableOn: string;
  category: string;
  chargeTaxes: boolean;
  collections: string[];
  description: string;
  name: string;
  price: number;
  productType: {
    label: string;
    value: {
      hasVariants: boolean;
      id: string;
      name: string;
      productAttributes: {
        edges: Array<{ node: AttributeType }>;
      };
    };
  };
  seoDescription: string;
  seoTitle: string;
  sku: string;
  stockQuantity: number;
}
interface ProductCreatePageProps {
  errors: UserError[];
  collections?: Array<{
    id: string;
    name: string;
  }>;
  currency: string;
  categories?: Array<{
    id: string;
    name: string;
  }>;
  disabled: boolean;
  productTypes?: Array<{
    id: string;
    name: string;
    hasVariants: boolean;
    productAttributes: {
      edges: Array<{
        node: AttributeType;
      }>;
    };
  }>;
  header: string;
  saveButtonBarState?: SaveButtonBarState;
  onAttributesEdit: () => void;
  onBack?();
  onSubmit?(data: FormData);
}

const decorate = withStyles(theme => ({
  cardContainer: {
    marginTop: theme.spacing.unit * 2,
    [theme.breakpoints.down("sm")]: {
      marginTop: theme.spacing.unit
    }
  },
  root: {
    display: "grid",
    gridGap: theme.spacing.unit * 2 + "px",
    gridTemplateColumns: "9fr 4fr",
    marginTop: theme.spacing.unit * 2,
    [theme.breakpoints.down("sm")]: {
      gridGap: theme.spacing.unit + "px",
      gridTemplateColumns: "1fr",
      marginTop: theme.spacing.unit
    }
  }
}));

export const ProductCreatePage = decorate<ProductCreatePageProps>(
  ({
    classes,
    currency,
    disabled,
    categories,
    collections,
    errors: userErrors,
    header,
    productTypes,
    saveButtonBarState,
    onAttributesEdit,
    onBack,
    onSubmit
  }) => {
    const initialData: FormData = {
      attributes: [],
      available: false,
      availableOn: "",
      category: "",
      chargeTaxes: false,
      collections: [],
      description: "",
      name: "",
      price: 0,
      productType: {
        label: "",
        value: {
          hasVariants: false,
          id: "",
          name: "",
          productAttributes: {
            edges: [] as Array<{ node: AttributeType }>
          }
        }
      },
      seoDescription: "",
      seoTitle: "",
      sku: null,
      stockQuantity: null
    };
    return (
      <Form onSubmit={onSubmit} errors={userErrors} initial={initialData}>
        {({ change, data, errors, hasChanged, submit }) => (
          <Container width="md">
            <PageHeader title={header} onBack={onBack} />
            <div className={classes.root}>
              <div>
                <ProductDetailsForm
                  data={data}
                  disabled={disabled}
                  errors={errors}
                  onChange={change}
                />
                <div className={classes.cardContainer}>
                  <ProductPricing
                    currency={currency}
                    data={data}
                    disabled={disabled}
                    onChange={change}
                  />
                </div>
                <div className={classes.cardContainer}>
                  <SeoForm
                    helperText={i18n.t(
                      "Add search engine title and description to make this product easier to find"
                    )}
                    title={data.seoTitle}
                    titlePlaceholder={data.name}
                    description={data.seoDescription}
                    descriptionPlaceholder={data.description}
                    loading={disabled}
                    onChange={change}
                  />
                </div>
              </div>
              <div>
                <ProductOrganization
                  category={data.category}
                  categories={
                    categories !== undefined && categories !== null
                      ? categories.map(category => ({
                          label: category.name,
                          value: category.id
                        }))
                      : []
                  }
                  errors={errors}
                  productCollections={data.collections}
                  collections={
                    collections !== undefined && collections !== null
                      ? collections.map(collection => ({
                          label: collection.name,
                          value: collection.id
                        }))
                      : []
                  }
                  productTypes={productTypes}
                  data={data}
                  disabled={disabled}
                  onChange={change}
                />
                <div className={classes.cardContainer}>
                  <ProductAvailabilityForm
                    data={data}
                    errors={errors}
                    loading={disabled}
                    onChange={change}
                  />
                </div>
              </div>
            </div>
            <SaveButtonBar
              labels={{
                delete: i18n.t("Remove product"),
                save: i18n.t("Save product")
              }}
              onCancel={onBack}
              onSave={submit}
              state={saveButtonBarState}
              disabled={disabled || !onSubmit || !hasChanged}
            />
          </Container>
        )}
      </Form>
    );
  }
);
export default ProductCreatePage;
