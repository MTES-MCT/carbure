import { CBQueryParams } from "common/hooks/query-builder-2"
import {
  PathsApiTiruertOperationsBalanceFiltersGetParametersQueryFilter as BalancesFilter,
  PathsApiTiruertOperationsBalanceGetParametersQueryGroup_by as BalancesGroupBy,
} from "api-schema"
import { apiTypes } from "common/services/api-fetch.types"
import {
  OperationBiofuelCategory,
  OperationSector,
  OperationsStatus,
} from "accounting/types"

export { BalancesFilter, BalancesGroupBy }
export type Balance = apiTypes["Balance"]

export interface BalancesQuery
  extends Omit<CBQueryParams<[], OperationsStatus[], string[]>, "type"> {
  [BalancesFilter.sector]?: OperationSector[]
  [BalancesFilter.customs_category]?: OperationBiofuelCategory[]
  [BalancesFilter.biofuel]?: string[]
}
