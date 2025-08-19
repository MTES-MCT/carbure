/**
 * Common types used in the accounting module
 */
import { apiTypes } from "common/services/api-fetch.types"
import {
  PathsApiTiruertOperationsGetParametersQueryStatus as OperationsStatus,
  PathsApiTiruertOperationsGetParametersQuerySector as OperationSector,
  PathsApiTiruertOperationsGetParametersQueryOperation as OperationType,
  PathsApiTiruertOperationsFiltersGetParametersQueryFilter as OperationsFilter,
  PathsApiTiruertElecOperationsGetParametersQueryType as OperationDebitOrCredit,
  PathsApiTiruertOperationsGetParametersQueryCustoms_category as OperationBiofuelCategory,
  PathsApiTiruertOperationsGetParametersQueryOrder_by as OperationOrder,
  OperationTypeEnum as CreateOperationType,
  PathsApiTiruertOperationsBalanceGetParametersQueryGroup_by as BalancesGroupBy,
  PathsApiTiruertOperationsBalanceFiltersGetParametersQueryFilter as BalancesFilter,
  PathsApiTiruertElecOperationsGetParametersQueryStatus as ElecOperationsStatus,
  PathsApiTiruertElecOperationsGetParametersQueryOperation as ElecOperationType,
  PathsApiTiruertElecOperationsGetParametersQueryOrder_by as ElecOperationOrder,
  PathsApiTiruertElecOperationsFiltersGetParametersQueryFilter as ElecOperationsFilter,
  ElecOperationTypeEnum as CreateElecOperationType,
} from "api-schema"
import { QueryBuilder } from "common/hooks/new-query-builder"

// Type definitions
export type Operation = apiTypes["OperationList"] & {
  quantity_renewable: number
}

export type Balance = apiTypes["Balance"]

export type OperationsQueryBuilder = QueryBuilder<
  OperationsStatus[],
  OperationOrder[]
>
export type OperationsQuery = OperationsQueryBuilder["query"] & {
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
  OperationOrder,
  ElecOperationOrder,
}

/** BALANCES */

export { BalancesFilter }
export type BalancesQueryBuilder = QueryBuilder<OperationsStatus[]>
export type BalancesQuery = BalancesQueryBuilder["query"] & {
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

export type ElecOperationsQueryBuilder = QueryBuilder<
  ElecOperationsStatus[],
  ElecOperationOrder[]
>
export type ElecOperationsQuery = ElecOperationsQueryBuilder["query"] & {
  [OperationsFilter.type]?: OperationDebitOrCredit[]
  [OperationsFilter.operation]?: ElecOperationType[]
}

export {
  ElecOperationsStatus,
  ElecOperationType,
  ElecOperationsFilter,
  CreateElecOperationType,
}
