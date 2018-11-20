import { withStyles, WithStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import * as React from "react";

import { CardMenu } from "../../../components/CardMenu/CardMenu";
import { CardSpacer } from "../../../components/CardSpacer";
import { Container } from "../../../components/Container";
import DateFormatter from "../../../components/DateFormatter";
import PageHeader from "../../../components/PageHeader";
import Skeleton from "../../../components/Skeleton";
import i18n from "../../../i18n";
import { maybe, renderCollection } from "../../../misc";
import { UserError } from "../../../types";
import { OrderStatus } from "../../../types/globalTypes";
import { OrderDetails_order } from "../../types/OrderDetails";
import OrderCustomer from "../OrderCustomer";
import OrderFulfillment from "../OrderFulfillment";
import OrderHistory, { FormData as HistoryFormData } from "../OrderHistory";
import OrderPayment from "../OrderPayment/OrderPayment";
import OrderUnfulfilledItems from "../OrderUnfulfilledItems/OrderUnfulfilledItems";

export interface OrderDetailsPageProps {
  order: OrderDetails_order;
  shippingMethods?: Array<{
    id: string;
    name: string;
  }>;
  countries?: Array<{
    code: string;
    label: string;
  }>;
  errors: UserError[];
  onBack();
  onBillingAddressEdit();
  onFulfillmentCancel(id: string);
  onFulfillmentTrackingNumberUpdate(id: string);
  onOrderFulfill();
  onProductClick?(id: string);
  onPaymentCapture();
  onPaymentPaid();
  onPaymentRefund();
  onPaymentVoid();
  onShippingAddressEdit();
  onOrderCancel();
  onNoteAdd(data: HistoryFormData);
}
interface OrderDetailsPageState {
  openedBillingAddressEditDialog: boolean;
  openedFulfillmentDialog: boolean;
  openedPaymentCaptureDialog: boolean;
  openedPaymentPaidDialog: boolean;
  openedPaymentRefundDialog: boolean;
  openedPaymentVoidDialog: boolean;
  openedShippingAddressEditDialog: boolean;
}

const decorate = withStyles(theme => ({
  date: {
    marginBottom: theme.spacing.unit * 3,
    marginLeft: theme.spacing.unit * 7
  },
  header: {
    marginBottom: 0
  },
  menu: {
    marginRight: -theme.spacing.unit
  },
  root: {
    display: "grid",
    gridColumnGap: theme.spacing.unit * 2 + "px",
    gridTemplateColumns: "9fr 4fr"
  }
}));
class OrderDetailsPageComponent extends React.Component<
  OrderDetailsPageProps & WithStyles<"date" | "header" | "menu" | "root">,
  OrderDetailsPageState
> {
  state = {
    openedBillingAddressEditDialog: false,
    openedFulfillmentDialog: false,
    openedPaymentCaptureDialog: false,
    openedPaymentPaidDialog: false,
    openedPaymentRefundDialog: false,
    openedPaymentVoidDialog: false,
    openedShippingAddressEditDialog: false
  };

  toggleFulfillmentDialog = () =>
    this.setState(prevState => ({
      openedFulfillmentDialog: !prevState.openedFulfillmentDialog
    }));
  togglePaymentVoidDialog = () =>
    this.setState(prevState => ({
      openedPaymentVoidDialog: !prevState.openedPaymentVoidDialog
    }));
  togglePaymentCaptureDialog = () =>
    this.setState(prevState => ({
      openedPaymentCaptureDialog: !prevState.openedPaymentCaptureDialog
    }));
  togglePaymentRefundDialog = () =>
    this.setState(prevState => ({
      openedPaymentRefundDialog: !prevState.openedPaymentRefundDialog
    }));
  toggleShippingAddressEditDialog = () =>
    this.setState(prevState => ({
      openedShippingAddressEditDialog: !prevState.openedShippingAddressEditDialog
    }));
  toggleBillingAddressEditDialog = () =>
    this.setState(prevState => ({
      openedBillingAddressEditDialog: !prevState.openedBillingAddressEditDialog
    }));
  togglePaymentPaidDialog = () =>
    this.setState(prevState => ({
      openedPaymentPaidDialog: !prevState.openedPaymentPaidDialog
    }));

  render() {
    const {
      classes,
      countries,
      errors,
      order,
      onBack,
      onBillingAddressEdit,
      onFulfillmentCancel,
      onFulfillmentTrackingNumberUpdate,
      onNoteAdd,
      onOrderCancel,
      onOrderFulfill,
      onPaymentCapture,
      onPaymentPaid,
      onPaymentRefund,
      onPaymentVoid,
      onShippingAddressEdit
    } = this.props;
    const {
      openedBillingAddressEditDialog,
      openedFulfillmentDialog,
      openedPaymentCaptureDialog,
      openedPaymentPaidDialog,
      openedPaymentRefundDialog,
      openedPaymentVoidDialog,
      openedShippingAddressEditDialog
    } = this.state;
    const canCancel = maybe(() => order.status) !== OrderStatus.CANCELED;
    const canEditAddresses = maybe(() => order.status) !== OrderStatus.CANCELED;
    const canFulfill = maybe(() => order.status) !== OrderStatus.CANCELED;
    const unfulfilled = maybe(() => order.lines, []).filter(
      line => line.quantityFulfilled < line.quantity
    );
    return (
      <Container width="md">
        <PageHeader
          className={classes.header}
          title={maybe(() => order.number) ? "#" + order.number : undefined}
          onBack={onBack}
        >
          {canCancel && (
            <CardMenu
              className={classes.menu}
              menuItems={[
                {
                  label: i18n.t("Cancel order", { context: "button" }),
                  onSelect: onOrderCancel
                }
              ]}
            />
          )}
        </PageHeader>
        <div className={classes.date}>
          {order && order.created ? (
            <Typography variant="caption">
              <DateFormatter date={order.created} />
            </Typography>
          ) : (
            <Skeleton style={{ width: "10em" }} />
          )}
        </div>
        <div className={classes.root}>
          <div>
            {unfulfilled.length > 0 && (
              <OrderUnfulfilledItems
                canFulfill={canFulfill}
                lines={unfulfilled}
                onFulfill={onOrderFulfill}
              />
            )}
            {renderCollection(
              maybe(() => order.fulfillments),
              (fulfillment, fulfillmentIndex) => (
                <React.Fragment key={fulfillment.id}>
                  {!(unfulfilled.length === 0 && fulfillmentIndex === 0) && (
                    <CardSpacer />
                  )}
                  <OrderFulfillment
                    fulfillment={fulfillment}
                    orderNumber={maybe(() => order.number)}
                    onOrderFulfillmentCancel={() =>
                      onFulfillmentCancel(fulfillment.id)
                    }
                    onTrackingCodeAdd={() =>
                      onFulfillmentTrackingNumberUpdate(fulfillment.id)
                    }
                  />
                </React.Fragment>
              )
            )}
            <CardSpacer />
            <OrderPayment
              order={order}
              onCapture={onPaymentCapture}
              onMarkAsPaid={onPaymentPaid}
              onRefund={onPaymentRefund}
              onVoid={onPaymentVoid}
            />
            <OrderHistory
              history={maybe(() => order.events)}
              onNoteAdd={onNoteAdd}
            />
          </div>
          <div>
            <OrderCustomer
              canEditAddresses={canEditAddresses}
              canEditCustomer={false}
              order={order}
              onBillingAddressEdit={onBillingAddressEdit}
              onShippingAddressEdit={onShippingAddressEdit}
            />
          </div>
        </div>
      </Container>
    );
  }
}
const OrderDetailsPage = decorate<OrderDetailsPageProps>(
  OrderDetailsPageComponent
);
OrderDetailsPage.displayName = "OrderDetailsPage";
export default OrderDetailsPage;
