import { Entity } from "carbure/types"
import { Order } from "common/components/table"
import { useMemo } from "react"



export interface QueryStates<TFilterSelection, TSnapshot> {
  entity: Entity
  year: number
  filters: TFilterSelection
  search?: string
  status: string
  selection: number[]
  page: number
  limit?: number
  order?: Order
  snapshot?: TSnapshot
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



export function useQueryBuilder<TFilterSelection, TSnapshot>(params: QueryStates<TFilterSelection, TSnapshot>) {
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
    }),
    [entity.id, status, search, limit, order, filters, page, year]
  )
}



