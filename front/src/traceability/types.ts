import {
  PathsApiTraceabilityActionsGetParametersQueryOrder_by,
  PathsApiTraceabilityActionsGetParametersQueryIndustry as ActionIndustry,
} from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"

export { PathsApiTraceabilityActionsFiltersGetParametersQueryFilter as ActionFilter } from "api-schema"

export type ActionOrderBy =
  PathsApiTraceabilityActionsGetParametersQueryOrder_by
export type Action = apiTypes["Action"]
export type ActionQueryBuilder = QueryBuilder<"", ActionOrderBy[]>
export type ActionQuery = Omit<ActionQueryBuilder["query"], "status">

export type ActionFixedQuery = {
  industry: ActionIndustry
  type?: apiTypes["ActionTypeEnum"][]
}

export { ActionIndustry }
