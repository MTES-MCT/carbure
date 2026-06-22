import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiStockPocActionsGetParametersQueryType as ActionType,
  PathsApiStockPocActionsGetParametersQueryStatus as ActionStatus,
} from "api-schema"

export type Action = apiTypes["Action"]
export type ActionCreateRequest = apiTypes["ActionCreateRequest"]

export { ActionType, ActionStatus }
