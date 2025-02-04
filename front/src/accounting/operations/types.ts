import {
  OperationSector,
  OperationsStatus,
  OperationType,
} from "accounting/types"
import {
  PathsApiTiruertOperationsFiltersGetParametersQueryFilter as OperationsFilter,
  PathsApiTiruertOperationsGetParametersQueryType as OperationDebitOrCredit,
  PathsApiTiruertOperationsGetParametersQueryCustoms_category as OperationBiofuelCategory,
} from "api-schema"
import { CBQueryParams } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"

export type Operation = apiTypes["OperationList"]

export { OperationsFilter, OperationDebitOrCredit, OperationBiofuelCategory }

export interface OperationsQuery
  extends CBQueryParams<[], OperationsStatus[], string[]> {
  [OperationsFilter.status]?: OperationsStatus[]
  [OperationsFilter.sector]?: OperationSector[]
  [OperationsFilter.customs_category]?: OperationBiofuelCategory[]
  [OperationsFilter.biofuel]?: string[]
  [OperationsFilter.type]?: OperationDebitOrCredit[]
  [OperationsFilter.operation]?: OperationType[]
  [OperationsFilter.depot]?: string[]
}
