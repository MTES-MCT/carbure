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
  PathsApiTiruertElecOperationsGetParametersQueryType as OperationDebitOrCredit,
  PathsApiTiruertOperationsGetParametersQueryCustoms_category as OperationBiofuelCategory,
  OperationTypeEnum as CreateOperationType,
  PathsApiTiruertOperationsBalanceGetParametersQueryGroup_by as BalancesGroupBy,
  PathsApiTiruertOperationsBalanceFiltersGetParametersQueryFilter as BalancesFilter,
  PathsApiTiruertElecOperationsGetParametersQueryStatus as ElecOperationsStatus,
  PathsApiTiruertElecOperationsGetParametersQueryOperation as ElecOperationType,
  PathsApiTiruertElecOperationsGetParametersQueryOrder_by as OperationOrderBy,
  PathsApiTiruertElecOperationsFiltersGetParametersQueryFilter as ElecOperationsFilter,
  ElecOperationTypeEnum as CreateElecOperationType,
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
  OperationOrderBy,
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

export type ElecOperation = apiTypes["ElecOperationList"]
export type ElecBalance = apiTypes["ElecBalance"]

export enum ElecOperationSector {
  ELEC = "ELEC",
}

export interface ElecOperationsQuery
  extends CBQueryParams<[], ElecOperationsStatus[], string[]> {
  [OperationsFilter.status]?: ElecOperationsStatus[]
  [OperationsFilter.type]?: OperationDebitOrCredit[]
  [OperationsFilter.operation]?: ElecOperationType[]
}

export {
  ElecOperationsStatus,
  ElecOperationType,
  ElecOperationsFilter,
  CreateElecOperationType,
}
