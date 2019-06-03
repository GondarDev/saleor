import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import {
  createStyles,
  Theme,
  withStyles,
  WithStyles
} from "@material-ui/core/styles";
import TextField from "@material-ui/core/TextField";
import * as React from "react";

import CardTitle from "../../../components/CardTitle";
import ControlledSwitch from "../../../components/ControlledSwitch";
import i18n from "../../../i18n";

const styles = (theme: Theme) =>
  createStyles({
    date: {
      "& svg": {
        fill: theme.palette.primary.main
      },
      marginTop: theme.spacing.unit * 4
    },
    expandedSwitchContainer: {
      marginBottom: 0
    },
    switchContainer: {
      marginBottom: -theme.spacing.unit
    }
  });

interface ProductAvailabilityFormProps extends WithStyles<typeof styles> {
  data: {
    available: boolean;
    publicationDate: string;
  };
  errors: { [key: string]: string };
  loading?: boolean;
  onChange(event: any);
}

export const ProductAvailabilityForm = withStyles(styles, {
  name: "ProductAvailabilityForm"
})(
  ({
    classes,
    data: { available, publicationDate },
    errors,
    loading,
    onChange
  }: ProductAvailabilityFormProps) => (
    <Card>
      <CardTitle title={i18n.t("Visibility")} />
      <CardContent>
        <div
          className={
            available
              ? classes.expandedSwitchContainer
              : classes.switchContainer
          }
        >
          <ControlledSwitch
            name="available"
            label={i18n.t("Visible")}
            uncheckedLabel={i18n.t("Hidden")}
            secondLabel={
              publicationDate
                ? available
                  ? i18n.t("since ") + publicationDate
                  : i18n.t("will be visible on ") + publicationDate
                : null
            }
            checked={available}
            onChange={onChange}
            disabled={loading}
          />
        </div>
        {!available && (
          <>
            <TextField
              error={!!errors.publicationDate}
              disabled={loading}
              label={i18n.t("Publish on")}
              name="publicationDate"
              type="date"
              fullWidth={true}
              helperText={errors.publicationDate}
              value={publicationDate ? publicationDate : ""}
              onChange={onChange}
              className={classes.date}
              InputLabelProps={{
                shrink: true
              }}
            />
          </>
        )}
      </CardContent>
    </Card>
  )
);
ProductAvailabilityForm.displayName = "ProductAvailabilityForm";
export default ProductAvailabilityForm;
