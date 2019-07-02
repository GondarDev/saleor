import { storiesOf } from "@storybook/react";
import React from "react";

import SingleSelectField from "@saleor/components/SingleSelectField";
import CardDecorator from "../../CardDecorator";
import Decorator from "../../Decorator";

const choices = [
  { value: "1", label: "Apparel" },
  { value: "2", label: "Groceries" },
  { value: "3", label: "Books" },
  { value: "4", label: "Accessories" }
];

storiesOf("Generics / SingleSelectField", module)
  .addDecorator(CardDecorator)
  .addDecorator(Decorator)
  .add("with no value", () => (
    <SingleSelectField choices={choices} onChange={undefined} />
  ))
  .add("with value", () => (
    <SingleSelectField
      choices={choices}
      onChange={undefined}
      value={choices[0].value}
    />
  ))
  .add("with label", () => (
    <SingleSelectField
      choices={choices}
      onChange={undefined}
      label="Lorem ipsum"
    />
  ))
  .add("with hint", () => (
    <SingleSelectField
      choices={choices}
      onChange={undefined}
      hint="Lorem ipsum"
    />
  ))
  .add("with label and hint", () => (
    <SingleSelectField
      choices={choices}
      onChange={undefined}
      label="Lorem"
      hint="Ipsum"
    />
  ))
  .add("with value, label and hint", () => (
    <SingleSelectField
      choices={choices}
      onChange={undefined}
      value={choices[0].value}
      label="Lorem"
      hint="Ipsum"
    />
  ))
  .add("with error hint", () => (
    <SingleSelectField
      choices={choices}
      onChange={undefined}
      hint="Lorem error"
      error={true}
    />
  ));
