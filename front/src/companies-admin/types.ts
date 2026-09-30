import { QueryBuilder } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiEntitiesAdminUsersFiltersGetParametersQueryFilter as AdminUserQueryFilter,
  PathsApiEntitiesAdminUsersGetParametersQueryEntity_type as AdminUserQueryEntityType,
  PathsApiEntitiesAdminUsersGetParametersQueryRole as AdminUserQueryRole,
  PathsApiElecTransferCertificatesGetParametersQueryUsed_in_tiruert as AdminUserQueryIsActive,
} from "api-schema"

export type EntityDetails = apiTypes["EntityMetrics"]

export type AdminUserQueryBuilder = QueryBuilder<undefined, undefined>
export type AdminUserQuery = AdminUserQueryBuilder["query"] & {
  [AdminUserQueryFilter.entity_type]?: AdminUserQueryEntityType[]
  [AdminUserQueryFilter.role]?: AdminUserQueryRole[]
  [AdminUserQueryFilter.is_active]?: AdminUserQueryIsActive[]
}

export { AdminUserQueryFilter }
