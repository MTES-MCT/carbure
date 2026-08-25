import { apiTypes } from "common/services/api-fetch.types"
import { QueryBuilder } from "common/hooks/query-builder-2"
import { PathsApiH2StationsGetParametersQueryOrder_by } from "api-schema"

export {
  PathsApiH2StationsGetParametersQueryAccess_type as AccessType,
  DistributedPressureEnum as DistributedPressure,
  PathsApiH2StationsGetParametersQueryOrder_by,
  PathsApiH2StationsFiltersGetParametersQueryFilter as H2StationFilter,
} from "api-schema"

export type H2Station = apiTypes["H2Station"]
export type H2StationInputRequest = apiTypes["H2StationInputRequest"]

export type H2StationOrder = PathsApiH2StationsGetParametersQueryOrder_by
export type H2StationsQueryBuilder = QueryBuilder<"", H2StationOrder[]>
export type H2StationsQuery = H2StationsQueryBuilder["query"]
