import { MutationResult } from "react-apollo";

export interface UserError {
  field: string;
  message: string;
}

export interface ListProps {
  disabled: boolean;
  pageInfo?: {
    hasNextPage: boolean;
    hasPreviousPage: boolean;
  };
  onNextPage: () => void;
  onPreviousPage: () => void;
  onRowClick: (id: string) => () => void;
}
export type ListAction = (ids: string[]) => void;
export interface ListActions {
  toggle: (id: string) => void;
  isChecked: (id: string) => boolean;
  selected: number;
  toolbar: React.ReactNode | React.ReactNodeArray;
}
export type ListActionProps<TActions extends string> = Record<
  TActions,
  ListAction
>;
export interface PageListProps extends ListProps {
  onAdd: () => void;
}

export interface PartialMutationProviderOutput<
  TData extends {} = {},
  TVariables extends {} = {}
> {
  opts: MutationResult<TData>;
  mutate: (variables: TVariables) => void;
}

export type FormErrors<TKeys extends string> = Partial<Record<TKeys, string>>;

export type Pagination = Partial<{
  after: string;
  before: string;
}>;

export type Dialog<TDialog extends string> = Partial<{
  action: TDialog;
}>;
export type ActiveTab<TTab extends string> = Partial<{
  activeTab: TTab;
}>;
export type SingleAction = Partial<{
  id: string;
}>;
