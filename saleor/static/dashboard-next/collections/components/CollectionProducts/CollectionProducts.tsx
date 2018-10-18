import Button from "@material-ui/core/Button";
import Card from "@material-ui/core/Card";
import { withStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableFooter from "@material-ui/core/TableFooter";
import TableHead from "@material-ui/core/TableHead";
import TableRow from "@material-ui/core/TableRow";
import * as React from "react";

import { PageListProps } from "../../..";
import CardTitle from "../../../components/CardTitle";
import Skeleton from "../../../components/Skeleton";
import StatusLabel from "../../../components/StatusLabel";
import TableCellAvatar from "../../../components/TableCellAvatar";
import TablePagination from "../../../components/TablePagination";
import i18n from "../../../i18n";
import { maybe, renderCollection } from "../../../misc";
import { CollectionDetails_collection } from "../../types/CollectionDetails";

export interface CollectionProductsProps extends PageListProps {
  collection: CollectionDetails_collection;
}

const decorate = withStyles({
  tableRow: {
    cursor: "pointer" as "pointer"
  },
  textCenter: {
    textAlign: "center" as "center"
  }
});
const CollectionProducts = decorate<CollectionProductsProps>(
  ({
    classes,
    collection,
    disabled,
    onAdd,
    onNextPage,
    onPreviousPage,
    onRowClick,
    pageInfo
  }) => (
    <Card>
      <CardTitle
        title={
          !!collection ? (
            i18n.t("Products in {{ collectionName }}", {
              collectionName: collection.name
            })
          ) : (
            <Skeleton />
          )
        }
        toolbar={
          <Button
            disabled={disabled}
            variant="flat"
            color="secondary"
            onClick={onAdd}
          >
            {i18n.t("Assign product", {
              context: "button"
            })}
          </Button>
        }
      />
      <Table>
        <TableHead>
          <TableRow>
            <TableCell />
            <TableCell>{i18n.t("Name", { context: "table header" })}</TableCell>
            <TableCell className={classes.textCenter}>
              {i18n.t("Type", { context: "table header" })}
            </TableCell>
            <TableCell>
              {i18n.t("Published", { context: "table header" })}
            </TableCell>
          </TableRow>
        </TableHead>
        <TableFooter>
          <TableRow>
            <TablePagination
              colSpan={4}
              hasNextPage={pageInfo.hasNextPage}
              onNextPage={onNextPage}
              hasPreviousPage={pageInfo.hasPreviousPage}
              onPreviousPage={onPreviousPage}
            />
          </TableRow>
        </TableFooter>
        <TableBody>
          {renderCollection(
            maybe(() => collection.products.edges.map(edge => edge.node)),
            product => (
              <TableRow
                className={classes.tableRow}
                hover={!!product}
                onClick={!!product ? onRowClick(product.id) : undefined}
                key={product ? product.id : "skeleton"}
              >
                <TableCellAvatar
                  thumbnail={maybe(() => product.thumbnailUrl)}
                />
                <TableCell>
                  {maybe<React.ReactNode>(() => product.name, <Skeleton />)}
                </TableCell>
                <TableCell className={classes.textCenter}>
                  {maybe<React.ReactNode>(
                    () => product.productType.name,
                    <Skeleton />
                  )}
                </TableCell>
                <TableCell>
                  {maybe(
                    () => (
                      <StatusLabel
                        label={
                          product.isPublished
                            ? i18n.t("Published")
                            : i18n.t("Not published")
                        }
                        status={product.isPublished ? "success" : "error"}
                      />
                    ),
                    <Skeleton />
                  )}
                </TableCell>
              </TableRow>
            ),
            () => (
              <TableRow>
                <TableCell />
                <TableCell colSpan={3}>{i18n.t("No products found")}</TableCell>
              </TableRow>
            )
          )}
        </TableBody>
      </Table>
    </Card>
  )
);
CollectionProducts.displayName = "CollectionProducts";
export default CollectionProducts;
