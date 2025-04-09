/**
 * Common types used in the accounting module
 */
import { CBQueryParams } from "common/hooks/query-builder-2"
import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiTiruertOperationsGetParametersQueryStatus as OperationsStatus,
  PathsApiTiruertOperationsGetParametersQuerySector as OperationSector,
  PathsApiTiruertOperationsGetParametersQueryOperation as OperationType,
  PathsApiTiruertOperationsFiltersGetParametersQueryFilter as OperationsFilter,
  PathsApiTiruertOperationsGetParametersQueryType as OperationDebitOrCredit,
  PathsApiTiruertOperationsGetParametersQueryCustoms_category as OperationBiofuelCategory,
  OperationTypeEnum as CreateOperationType,
  PathsApiTiruertOperationsBalanceGetParametersQueryGroup_by as BalancesGroupBy,
  PathsApiTiruertOperationsBalanceFiltersGetParametersQueryFilter as BalancesFilter,
} from "api-schema"

// Type definitions
export type Operation = apiTypes["OperationList"]
export type Balance = apiTypes["Balance"]
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

// Re-exports
export {
  OperationsStatus,
  OperationSector,
  OperationType, // List of operation types including ACQUISITION which is just used for display
  CreateOperationType,
  OperationsFilter,
  OperationDebitOrCredit,
  OperationBiofuelCategory,
  BalancesGroupBy,
}

/** BALANCES */

export { BalancesFilter }
export interface BalancesQuery
  extends Omit<CBQueryParams<[], OperationsStatus[], string[]>, "type"> {
  [BalancesFilter.sector]?: OperationSector[]
  [BalancesFilter.customs_category]?: OperationBiofuelCategory[]
  [BalancesFilter.biofuel]?: string[]
}

// For operations and balances, we want to display specific views for each sector
export enum SectorTabs {
  BIOFUELS = "biofuels",
  ELEC = "elec",
}
