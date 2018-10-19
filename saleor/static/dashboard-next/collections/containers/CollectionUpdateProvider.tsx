import * as React from "react";

import { TypedCollectionUpdateMutation } from "../mutations";
import {
  CollectionUpdate,
  CollectionUpdateVariables
} from "../types/CollectionUpdate";

import {
  PartialMutationProviderProps,
  PartialMutationProviderRenderProps
} from "../..";

interface CollectionUUpdateProviderProps
  extends PartialMutationProviderProps<CollectionUpdate> {
  children: PartialMutationProviderRenderProps<
    CollectionUpdate,
    CollectionUpdateVariables
  >;
}

const CollectionUUpdateProvider: React.StatelessComponent<
  CollectionUUpdateProviderProps
> = ({ children, onError, onSuccess }) => (
  <TypedCollectionUpdateMutation onCompleted={onSuccess} onError={onError}>
    {(mutate, { data, error, loading }) =>
      children({
        data,
        error,
        loading,
        mutate
      })
    }
  </TypedCollectionUpdateMutation>
);

export default CollectionUUpdateProvider;
