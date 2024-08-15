import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import { ElecAdminProvisionCertificateFilter } from "elec-admin/types"
import { useMemo } from "react"


export type SnapshotType = Record<string, number>

export type FilterSelectionType = Record<string, string[]>

export interface QueryStates {
  entity: Entity
  year: number
  filters: FilterSelectionType
  search?: string
  status: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: SnapshotType
}


interface BaseQuery {
  entity_id: number;
  year: number;
  status: string;
  search?: string;
  from_idx: number;
  limit?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}



export function useQueryBuilder(params: QueryStates) {
  const {
    entity,
    year,
    status,
    search,
    page = 0,
    limit,
    order,
    filters,
  } = params;

  return useMemo<BaseQuery>(
    () => ({
      entity_id: entity.id,
      year,
      status,
      search,
      from_idx: page * (limit ?? 0),
      limit: limit || undefined,
      sort_by: order?.column,
      order: order?.direction,
      ...filters,
    } as BaseQuery),
    [entity.id, status, search, limit, order, filters, page, year]
  )
}



