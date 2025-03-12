import { CBQueryParams } from "common/hooks/query-builder-2"
import { PathsApiTiruertOperationsBalanceFiltersGetParametersQueryFilter as BalancesFilter } from "api-schema"
import {
  OperationBiofuelCategory,
  OperationSector,
  OperationsStatus,
} from "accounting/types"

export { BalancesFilter }

export interface BalancesQuery
  extends Omit<CBQueryParams<[], OperationsStatus[], string[]>, "type"> {
  [BalancesFilter.sector]?: OperationSector[]
  [BalancesFilter.customs_category]?: OperationBiofuelCategory[]
  [BalancesFilter.biofuel]?: string[]
}
