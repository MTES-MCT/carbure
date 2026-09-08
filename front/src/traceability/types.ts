import {
  PathsApiTraceabilityActionsGetParametersQueryOrder_by as ActionOrderBy,
  PathsApiTraceabilityActionsGetParametersQueryStatus as ActionStatus,
  PathsApiTraceabilityActionsFiltersGetParametersQueryFilter as ActionFilter,
  PathsApiTraceabilityActionsGetParametersQueryShipping_method as ActionShippingMethod,
  PathsApiTraceabilityActionsGetParametersQueryType as ActionType,
} from "api-schema"
export { PathsApiTraceabilityActionsGetParametersQueryIndustry as ActionIndustry } from "api-schema"
import { QueryBuilder } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"

export type Action = apiTypes["Action"]
export type ActionHolder = NonNullable<Action["holder"]>
export type ActionMaterial = NonNullable<Action["material"]>
export type ActionSite = NonNullable<Action["site"]>

export type ActionQueryBuilder = QueryBuilder<ActionStatus[], ActionOrderBy[]>

export type ActionQuery = ActionQueryBuilder["query"] & {
  [ActionFilter.holder]?: string[]
  [ActionFilter.type]?: ActionType[]
  [ActionFilter.material]?: string[]
  [ActionFilter.shipping_method]?: ActionShippingMethod[]
  [ActionFilter.site]?: string[]
}

export {
  ActionType,
  ActionStatus,
  ActionShippingMethod,
  ActionFilter,
  ActionOrderBy,
}
