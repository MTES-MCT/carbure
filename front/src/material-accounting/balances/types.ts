import { CBQueryParams } from "common/hooks/query-builder-2"
import {
  OperationBiofuelCategory,
  OperationSector,
  OperationsFilter,
  OperationsStatus,
} from "material-accounting/operations/types"
import { apiTypes } from "common/services/api-fetch.types"

export type Balance = apiTypes["Balance"]

export interface BalancesQuery
  extends CBQueryParams<[], OperationsStatus[], string[]> {
  [OperationsFilter.sector]?: OperationSector[]
  [OperationsFilter.customs_category]?: OperationBiofuelCategory[]
  [OperationsFilter.biofuel]?: string[]
}
