import { API } from "basebuild/packages/client/src/api"
import {
  authStore,
  notificationStore,
  routeStore,
  screenStore,
  builderStore,
  uploadStore,
  rowSelectionStore,
  componentStore,
  currentRole,
  environmentStore,
  sidePanelStore,
  dndIsDragging,
} from "basebuild/packages/client/src/stores"
import { styleable } from "basebuild/packages/client/src/utils/styleable"
import { linkable } from "basebuild/packages/client/src/utils/linkable"
import { getAction } from "basebuild/packages/client/src/utils/getAction"
import Provider from "basebuild/packages/client/src/components/context/Provider.svelte"
import { ActionTypes } from "./constants"
import { fetchDatasourceSchema } from "./utils/schema.js"
import { getAPIKey } from "./utils/api.js"

export default {
  API,
  authStore,
  notificationStore,
  routeStore,
  rowSelectionStore,
  screenStore,
  builderStore,
  uploadStore,
  componentStore,
  environmentStore,
  sidePanelStore,
  dndIsDragging,
  currentRole,
  styleable,
  linkable,
  getAction,
  fetchDatasourceSchema,
  Provider,
  ActionTypes,
  getAPIKey,
}
