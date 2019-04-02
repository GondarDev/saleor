import * as React from "react";

import AppHeader from "../../../components/AppHeader";
import CardSpacer from "../../../components/CardSpacer";
import { ConfirmButtonTransitionState } from "../../../components/ConfirmButton";
import Container from "../../../components/Container";
import PageHeader from "../../../components/PageHeader";
import i18n from "../../../i18n";
import { maybe } from "../../../misc";
import { ProductTypeTranslationFragment } from "../../types/ProductTypeTranslationFragment";
import TranslationFields from "../TranslationFields";

export interface TranslationsProductTypesPageProps {
  activeField: string;
  disabled: boolean;
  languageCode: string;
  productType: ProductTypeTranslationFragment;
  saveButtonState: ConfirmButtonTransitionState;
  onBack: () => void;
  onEdit: (field: string) => void;
  onSubmit: (field: string, data: string) => void;
}

export const fieldNames = {
  attribute: "attribute",
  value: "attributeValue"
};

const TranslationsProductTypesPage: React.StatelessComponent<
  TranslationsProductTypesPageProps
> = ({
  activeField,
  disabled,
  languageCode,
  productType,
  saveButtonState,
  onBack,
  onEdit,
  onSubmit
}) => (
  <Container>
    <AppHeader onBack={onBack}>{i18n.t("Translations")}</AppHeader>
    <PageHeader
      title={i18n.t(
        'Translation Product Type "{{ productTypeName }}" - {{ languageCode }}',
        {
          context: "productType translation page title",
          languageCode,
          productTypeName: maybe(() => productType.name, "...")
        }
      )}
    />
    {maybe(() => productType.productAttributes, []).map(
      (attribute, attributeIndex) => (
        <>
          <TranslationFields
            activeField={activeField}
            disabled={disabled}
            initialState={false}
            title={i18n.t("Product Attribute ({{ attributeName }})", {
              attributeName: attribute.name
            })}
            fields={[
              {
                displayName: i18n.t("Attribute Name"),
                name: fieldNames.attribute + ":" + attribute.id,
                translation: maybe(() =>
                  attribute.translation ? attribute.translation.name : null
                ),
                type: "short" as "short",
                value: maybe(() => attribute.name)
              },
              ...attribute.values.map(
                (attributeValue, attributeValueIndex) => ({
                  displayName: i18n.t("Value {{ number }}", {
                    number: attributeValueIndex + 1
                  }),
                  name: fieldNames.value + ":" + attributeValue.id,
                  translation: maybe(() =>
                    attributeValue.translation
                      ? attributeValue.translation.name
                      : null
                  ),
                  type: "short" as "short",
                  value: maybe(() => attributeValue.name)
                })
              )
            ]}
            saveButtonState={saveButtonState}
            onEdit={onEdit}
            onSubmit={onSubmit}
          />
          {attributeIndex < productType.productAttributes.length - 1 && (
            <CardSpacer />
          )}
        </>
      )
    )}
    {
      <>
        <CardSpacer />
        {maybe(() => productType.variantAttributes, []).map(
          (attribute, attributeIndex) => (
            <>
              <TranslationFields
                activeField={activeField}
                disabled={disabled}
                initialState={false}
                title={i18n.t("Variant Attribute ({{ attributeName }})", {
                  attributeName: attribute.name
                })}
                fields={[
                  {
                    displayName: i18n.t("Attribute Name"),
                    name: fieldNames.attribute + ":" + attribute.id,
                    translation: maybe(() =>
                      attribute.translation ? attribute.translation.name : null
                    ),
                    type: "short" as "short",
                    value: maybe(() => attribute.name)
                  },
                  ...attribute.values.map(
                    (attributeValue, attributeValueIndex) => ({
                      displayName: i18n.t("Value {{ number }}", {
                        number: attributeValueIndex + 1
                      }),
                      name: fieldNames.value + ":" + attributeValue.id,
                      translation: maybe(() =>
                        attributeValue.translation
                          ? attributeValue.translation.name
                          : null
                      ),
                      type: "short" as "short",
                      value: maybe(() => attributeValue.name)
                    })
                  )
                ]}
                saveButtonState={saveButtonState}
                onEdit={onEdit}
                onSubmit={onSubmit}
              />
              {attributeIndex < productType.variantAttributes.length - 1 && (
                <CardSpacer />
              )}
            </>
          )
        )}
      </>
    }
  </Container>
);
TranslationsProductTypesPage.displayName = "TranslationsProductTypesPage";
export default TranslationsProductTypesPage;
