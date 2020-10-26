import { Filters } from "../../services/types"
import { EntitySelection } from "../helpers/use-entity"

import { usePageSelection } from "../../components/system/pagination" // prettier-ignore

import useUploadLotFile from "../actions/use-upload-file"
import useDuplicateLot from "../actions/use-duplicate-lots"
import useDeleteLots from "../actions/use-delete-lots"
import useValidateLots from "../actions/use-validate-lots"

import useFilterSelection from "../query/use-filters"
import useSearchSelection from "../query/use-search"
import useTransactionSelection from "../query/use-selection"
import useSortingSelection from "../query/use-sort-by"
import useStatusSelection from "../query/use-status"
import useYearSelection from "../query/use-year"
import useInvalidSelection from "../query/use-invalid"
import useDeadlineSelection from "../query/use-deadline"

import useGetSnapshot from "./use-snapshot"
import useGetLots from "./use-get-lots"

const initialFilters = {
  [Filters.Biocarburants]: null,
  [Filters.MatieresPremieres]: null,
  [Filters.CountriesOfOrigin]: null,
  [Filters.Periods]: null,
  [Filters.Clients]: null,
  [Filters.ProductionSites]: null,
  [Filters.DeliverySites]: null,
}

export default function useTransactions(entity: EntitySelection) {
  const pagination = usePageSelection()

  const invalid = useInvalidSelection(pagination)
  const deadline = useDeadlineSelection(pagination)
  const sorting = useSortingSelection(pagination)
  const search = useSearchSelection(pagination)
  const filters = useFilterSelection(initialFilters, pagination)
  const status = useStatusSelection(pagination, invalid, deadline)
  const year = useYearSelection(pagination, filters, invalid, deadline)

  const snapshot = useGetSnapshot(entity, year)
  const transactions = useGetLots(entity, status, filters, year, pagination, search, sorting, invalid, deadline) // prettier-ignore

  function refresh() {
    snapshot.getSnapshot()
    transactions.getTransactions()
  }

  const selection = useTransactionSelection(transactions.data?.lots)

  const uploader = useUploadLotFile(entity, refresh)
  const duplicator = useDuplicateLot(entity, refresh)
  const deleter = useDeleteLots(entity, selection, year, refresh)
  const validator = useValidateLots(entity, selection, year, refresh)

  return {
    entity,
    status,
    filters,
    year,
    pagination,
    snapshot,
    transactions,
    selection,
    search,
    invalid,
    deadline,
    sorting,
    deleter,
    uploader,
    duplicator,
    validator,
    refresh,
  }
}
