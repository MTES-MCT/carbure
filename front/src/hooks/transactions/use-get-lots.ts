import { useEffect } from "react"

import { Lots } from "../../services/types"
import { PageSelection } from "../../components/system/pagination"
import { EntitySelection } from "../helpers/use-entity"
import { FilterSelection } from "../query/use-filters"
import { SearchSelection } from "../query/use-search"
import { SortingSelection } from "../query/use-sort-by"
import { StatusSelection } from "../query/use-status"
import { YearSelection } from "../query/use-year"
import { InvalidSelection } from "../query/use-invalid"
import { DeadlineSelection } from "../query/use-deadline"

import * as api from "../../services/lots"
import useAPI from "../helpers/use-api"

export interface LotGetter {
  loading: boolean
  error: string | null
  data: Lots | null
  getTransactions: () => void
  exportAllTransactions: () => void
}

// fetches current transaction list when parameters change
export default function useGetLots(
  entity: EntitySelection,
  status: StatusSelection,
  filters: FilterSelection,
  year: YearSelection,
  pagination: PageSelection,
  search: SearchSelection,
  sorting: SortingSelection,
  invalid: InvalidSelection,
  deadline: DeadlineSelection
): LotGetter {
  const [transactions, resolveLots] = useAPI(api.getLots)

  function exportAllTransactions() {
    if (entity !== null) {
      api.downloadLots(
        status.active,
        entity.id,
        filters.selected,
        year.selected,
        search.query,
        sorting.column,
        sorting.order
      )
    }
  }

  function getTransactions() {
    if (entity !== null) {
      return resolveLots(
        status.active,
        entity.id,
        filters.selected,
        year.selected,
        pagination.page,
        pagination.limit,
        search.query,
        sorting.column,
        sorting.order,
        invalid.active,
        deadline.active
      ).cancel
    }
  }

  useEffect(getTransactions, [
    resolveLots,
    status.active,
    entity?.id,
    filters.selected,
    year.selected,
    pagination.page,
    pagination.limit,
    search.query,
    sorting.column,
    sorting.order,
    invalid.active,
    deadline.active,
  ])

  return { ...transactions, getTransactions, exportAllTransactions }
}

