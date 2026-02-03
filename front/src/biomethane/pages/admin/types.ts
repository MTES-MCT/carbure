import { apiTypes } from "common/services/api-fetch.types"
import { QueryBuilder } from "common/hooks/query-builder-2"
import {
  PathsApiBiomethaneAdminAnnualDeclarationsFiltersGetParametersQueryFilter as BiomethaneAdminAnnualDeclarationFilters,
  PathsApiBiomethaneAdminAnnualDeclarationsGetParametersQueryStatus as DashboardStatus,
} from "api-schema"

export { BiomethaneAdminAnnualDeclarationFilters, DashboardStatus }
export type BiomethaneProducer = apiTypes["BiomethaneProducer"]

export type BiomethaneAdminAnnualDeclaration =
  apiTypes["BiomethaneAdminAnnualDeclaration"]

export type BiomethaneAdminDashboardQueryBuilder = QueryBuilder<never, never>
export type BiomethaneAdminDashboardQuery =
  BiomethaneAdminDashboardQueryBuilder["query"]
