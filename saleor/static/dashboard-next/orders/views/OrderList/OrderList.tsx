import Button from "@material-ui/core/Button";
import * as React from "react";

import DeleteFilterTabDialog from "@saleor/components/DeleteFilterTabDialog";
import SaveFilterTabDialog, {
  SaveFilterTabDialogFormData
} from "@saleor/components/SaveFilterTabDialog";
import useBulkActions from "@saleor/hooks/useBulkActions";
import useDateLocalize from "@saleor/hooks/useDateLocalize";
import useNavigator from "@saleor/hooks/useNavigator";
import useNotifier from "@saleor/hooks/useNotifier";
import usePaginator, {
  createPaginationState
} from "@saleor/hooks/usePaginator";
import useShop from "@saleor/hooks/useShop";
import i18n from "@saleor/i18n";
import { getMutationState, maybe } from "@saleor/misc";
import OrderBulkCancelDialog from "../../components/OrderBulkCancelDialog";
import OrderListPage from "../../components/OrderListPage/OrderListPage";
import {
  TypedOrderBulkCancelMutation,
  TypedOrderDraftCreateMutation
} from "../../mutations";
import { TypedOrderListQuery } from "../../queries";
import { OrderBulkCancel } from "../../types/OrderBulkCancel";
import { OrderDraftCreate } from "../../types/OrderDraftCreate";
import {
  orderListUrl,
  OrderListUrlDialog,
  OrderListUrlFilters,
  OrderListUrlQueryParams,
  orderUrl
} from "../../urls";
import {
  areFiltersApplied,
  createFilter,
  createFilterChips,
  deleteFilterTab,
  getActiveFilters,
  getFilterTabs,
  getFilterVariables,
  saveFilterTab
} from "./filters";

interface OrderListProps {
  params: OrderListUrlQueryParams;
}

const PAGINATE_BY = 20;

export const OrderList: React.StatelessComponent<OrderListProps> = ({
  params
}) => {
  const formatDate = useDateLocalize();
  const navigate = useNavigator();
  const notify = useNotifier();
  const paginate = usePaginator();
  const shop = useShop();
  const { isSelected, listElements, reset, toggle, toggleAll } = useBulkActions(
    params.ids
  );

  const tabs = getFilterTabs();

  const currentTab =
    params.activeTab === undefined
      ? areFiltersApplied(params)
        ? tabs.length + 1
        : 0
      : parseInt(params.activeTab, 0);

  const closeModal = () =>
    navigate(
      orderListUrl({
        ...params,
        action: undefined,
        ids: undefined
      }),
      true
    );

  const changeFilters = (filters: OrderListUrlFilters) => {
    reset();
    navigate(orderListUrl(filters));
  };

  const changeFilterField = (filter: OrderListUrlFilters) => {
    reset();
    navigate(
      orderListUrl({
        ...getActiveFilters(params),
        ...filter,
        activeTab: undefined
      })
    );
  };

  const openModal = (action: OrderListUrlDialog, ids?: string[]) =>
    navigate(
      orderListUrl({
        ...params,
        action,
        ids
      })
    );

  const handleTabChange = (tab: number) =>
    navigate(
      orderListUrl({
        activeTab: tab.toString(),
        ...getFilterTabs()[tab - 1].data
      })
    );

  const handleFilterTabDelete = () => {
    deleteFilterTab(currentTab);
    reset();
    navigate(orderListUrl());
  };

  const handleFilterTabSave = (data: SaveFilterTabDialogFormData) => {
    saveFilterTab(data.name, getActiveFilters(params));
    handleTabChange(tabs.length + 1);
  };

  const paginationState = createPaginationState(PAGINATE_BY, params);
  const currencySymbol = maybe(() => shop.defaultCurrency, "USD");

  const handleCreateOrderCreateSuccess = (data: OrderDraftCreate) => {
    notify({
      text: i18n.t("Order draft succesfully created")
    });
    navigate(orderUrl(data.draftOrderCreate.order.id));
  };

  return (
    <TypedOrderDraftCreateMutation onCompleted={handleCreateOrderCreateSuccess}>
      {createOrder => (
        <TypedOrderListQuery
          displayLoader
          variables={{
            ...paginationState,
            filter: {
              ...getFilterVariables(params),
              customer: params.email
            }
          }}
        >
          {({ data, loading, refetch }) => {
            const { loadNextPage, loadPreviousPage, pageInfo } = paginate(
              maybe(() => data.orders.pageInfo),
              paginationState,
              params
            );

            const handleOrderBulkCancel = (data: OrderBulkCancel) => {
              if (data.orderBulkCancel.errors.length === 0) {
                notify({
                  text: i18n.t("Orders cancelled", {
                    context: "notification"
                  })
                });
                reset();
                refetch();
                closeModal();
              }
            };

            return (
              <TypedOrderBulkCancelMutation onCompleted={handleOrderBulkCancel}>
                {(orderBulkCancel, orderBulkCancelOpts) => {
                  const orderBulkCancelTransitionState = getMutationState(
                    orderBulkCancelOpts.called,
                    orderBulkCancelOpts.loading,
                    maybe(() => orderBulkCancelOpts.data.orderBulkCancel.errors)
                  );
                  const onOrderBulkCancel = (restock: boolean) =>
                    orderBulkCancel({
                      variables: {
                        ids: params.ids,
                        restock
                      }
                    });

                  return (
                    <>
                      <OrderListPage
                        currencySymbol={currencySymbol}
                        filtersList={createFilterChips(
                          params,
                          {
                            formatDate
                          },
                          changeFilterField
                        )}
                        currentTab={currentTab}
                        disabled={loading}
                        orders={maybe(() =>
                          data.orders.edges.map(edge => edge.node)
                        )}
                        pageInfo={pageInfo}
                        onAdd={createOrder}
                        onNextPage={loadNextPage}
                        onPreviousPage={loadPreviousPage}
                        onRowClick={id => () => navigate(orderUrl(id))}
                        isChecked={isSelected}
                        selected={listElements.length}
                        toggle={toggle}
                        toggleAll={toggleAll}
                        toolbar={
                          <Button
                            color="primary"
                            onClick={() => openModal("cancel", listElements)}
                          >
                            {i18n.t("Cancel", {
                              context: "cancel orders"
                            })}
                          </Button>
                        }
                        onSearchChange={query => changeFilterField({ query })}
                        onFilterAdd={filter =>
                          changeFilterField(createFilter(filter))
                        }
                        onFilterSave={() => openModal("save-search")}
                        onFilterDelete={() => openModal("delete-search")}
                        onTabChange={handleTabChange}
                        initialSearch={params.query || ""}
                        filterTabs={getFilterTabs()}
                        onAll={() =>
                          changeFilters({
                            status: undefined
                          })
                        }
                      />
                      <OrderBulkCancelDialog
                        confirmButtonState={orderBulkCancelTransitionState}
                        numberOfOrders={maybe(
                          () => params.ids.length.toString(),
                          "..."
                        )}
                        onClose={closeModal}
                        onConfirm={onOrderBulkCancel}
                        open={params.action === "cancel"}
                      />
                      <SaveFilterTabDialog
                        open={params.action === "save-search"}
                        confirmButtonState="default"
                        onClose={closeModal}
                        onSubmit={handleFilterTabSave}
                      />
                      <DeleteFilterTabDialog
                        open={params.action === "delete-search"}
                        confirmButtonState="default"
                        onClose={closeModal}
                        onSubmit={handleFilterTabDelete}
                        tabName={maybe(() => tabs[currentTab - 1].name, "...")}
                      />
                    </>
                  );
                }}
              </TypedOrderBulkCancelMutation>
            );
          }}
        </TypedOrderListQuery>
      )}
    </TypedOrderDraftCreateMutation>
  );
};

export default OrderList;
