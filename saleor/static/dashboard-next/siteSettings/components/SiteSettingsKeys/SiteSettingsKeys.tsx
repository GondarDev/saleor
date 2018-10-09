import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import IconButton from "@material-ui/core/IconButton";
import { withStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import DeleteIcon from "@material-ui/icons/Delete";
import * as React from "react";

import CardTitle from "../../../components/CardTitle";
import Skeleton from "../../../components/Skeleton";
import i18n from "../../../i18n";
import { maybe, renderCollection } from "../../../misc";
import { SiteSettings_shop_authorizationKeys } from "../../types/SiteSettings";

interface SiteSettingsKeysProps {
  disabled: boolean;
  keys: SiteSettings_shop_authorizationKeys[];
  onAdd: () => void;
  onRemove: (name: string) => void;
  onRowClick: (name: string) => void;
}

const decorate = withStyles(theme => ({
  iconCell: {
    "&:last-child": {
      paddingRight: 0
    },
    width: 48 + theme.spacing.unit / 2
  },
  row: {
    cursor: "pointer" as "pointer"
  }
}));
const SiteSettingsKeys = decorate<SiteSettingsKeysProps>(
  ({ classes, disabled, keys, onAdd, onRemove, onRowClick }) => (
    <Card>
      <CardTitle
        title={i18n.t("Authentication Keys", {
          context: "card title"
        })}
        toolbar={
          <Button
            color="secondary"
            disabled={disabled}
            variant="flat"
            onClick={onAdd}
          >
            {i18n.t("Add key", {
              context: "button"
            })}
          </Button>
        }
      />
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>
              {i18n.t("Authentication Type", { context: "table header" })}
            </TableCell>
            <TableCell>{i18n.t("Key", { context: "table header" })}</TableCell>
            <TableCell />
          </TableRow>
        </TableHead>
        <TableBody>
          {renderCollection(
            keys,
            key => (
              <TableRow
                className={classes.row}
                hover={!(disabled || !key)}
                key={maybe(() => key.name)}
                onClick={
                  !disabled && maybe(() => key.name)
                    ? () => onRowClick(key.name)
                    : undefined
                }
              >
                <TableCell>
                  {maybe(() => key.name) ? key.name : <Skeleton />}
                </TableCell>
                <TableCell>
                  {maybe(() => key.key) ? key.key : <Skeleton />}
                </TableCell>
                <TableCell className={classes.iconCell}>
                  <IconButton onClick={() => onRemove(key.name)}>
                    <DeleteIcon color="secondary" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ),
            () => (
              <TableRow>
                <TableCell colSpan={3}>{i18n.t("No keys")}</TableCell>
              </TableRow>
            )
          )}
        </TableBody>
      </Table>
    </Card>
  )
);
SiteSettingsKeys.displayName = "SiteSettingsKeys";
export default SiteSettingsKeys;
