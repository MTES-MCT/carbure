import {
  PathsApiTiruertOperationsFiltersGetParametersQueryFilter as OperationsFilter,
  PathsApiTiruertOperationsGetParametersQueryStatus as OperationsStatus,
} from "api-schema"
import { CBQueryParams } from "common/hooks/query-builder-2"

export { OperationsFilter, OperationsStatus }

export interface OperationsQuery
  extends CBQueryParams<[], OperationsStatus, undefined> {
  [OperationsFilter.statuses]?: OperationsStatus[]
  [OperationsFilter.sectors]?: string[]
  [OperationsFilter.categories]?: string[]
  [OperationsFilter.biofuels]?: string[]
  [OperationsFilter.operations]?: string[]
  [OperationsFilter.depots]?: string[]
}

export enum OperationType {
  INCORPORATION = "INCORPORATION",
  CESSION = "CESSION",
  MAC_BIO = "MAC_BIO",
  ACQUISITION = "ACQUISITION",
  TENEUR = "TENEUR",
}
