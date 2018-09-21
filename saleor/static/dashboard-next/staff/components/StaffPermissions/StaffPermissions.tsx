import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import { withStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import * as React from "react";

import CardTitle from "../../../components/CardTitle";
import { ControlledCheckbox } from "../../../components/ControlledCheckbox";
import Skeleton from "../../../components/Skeleton";
import i18n from "../../../i18n";
import { StaffMemberDetails_shop_permissions } from "../../types/StaffMemberDetails";

interface StaffPermissionsProps {
  permissions: StaffMemberDetails_shop_permissions[];
  data: {
    hasFullAccess: boolean;
    permissions: string[];
  };
  disabled: boolean;
  onChange: (event: React.ChangeEvent<any>) => void;
}

const decorate = withStyles(theme => ({
  checkbox: {
    marginBottom: theme.spacing.unit
  },
  hr: {
    backgroundColor: "#eaeaea",
    border: "none",
    height: 1,
    marginBottom: 0,
    marginTop: 0
  }
}));
const StaffPermissions = decorate<StaffPermissionsProps>(
  ({ classes, data, disabled, permissions, onChange }) => {
    const handleFullAccessChange = (event: React.ChangeEvent<any>) => {
      onChange(event);
      onChange({
        target: {
          name: "permissions",
          value: event.target.value ? permissions.map(perm => perm.code) : []
        }
      } as any);
    };
    const handlePermissionChange = (event: React.ChangeEvent<any>) => {
      onChange({
        target: {
          name: "permissions",
          value: event.target.value
            ? data.permissions.concat([event.target.name])
            : data.permissions.filter(perm => perm !== event.target.name)
        }
      } as any);
    };
    return (
      <Card>
        <CardTitle title={i18n.t("Permissions")} />
        <CardContent>
          <Typography>
            {i18n.t(
              "Expand or restrict user's permissions to access certain part of saleor system."
            )}
          </Typography>
          <ControlledCheckbox
            checked={data.hasFullAccess}
            disabled={disabled}
            label={i18n.t("User has full access to the store", {
              context: "checkbox label"
            })}
            name="hasFullAccess"
            onChange={handleFullAccessChange}
          />
        </CardContent>
        {!data.hasFullAccess && (
          <>
            <hr className={classes.hr} />
            <CardContent>
              {permissions === undefined ? (
                <Skeleton />
              ) : (
                permissions.map(perm => (
                  <ControlledCheckbox
                    checked={
                      data.permissions.filter(
                        userPerm => userPerm === perm.code
                      ).length === 1
                    }
                    disabled={disabled}
                    label={perm.name.replace(/\./, "")}
                    name={perm.code}
                    onChange={handlePermissionChange}
                    key={perm.code}
                  />
                ))
              )}
            </CardContent>
          </>
        )}
      </Card>
    );
  }
);
StaffPermissions.displayName = "StaffPermissions";
export default StaffPermissions;
