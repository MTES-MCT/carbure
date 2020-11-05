import React from "react"

import { Filters, Snapshot } from "../../services/types"
import { FilterSelection } from "../../hooks/query/use-filters"
import { SearchSelection } from "../../hooks/query/use-search"

import styles from "./transaction-filters.module.css"

import { SearchInput } from "../system"
import Select, { Option, SelectValue } from "../system/select"

const FILTER_ORDER = [
  Filters.Periods,
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.Clients,
  Filters.Vendors,
  Filters.CountriesOfOrigin,
  Filters.ProductionSites,
  Filters.DeliverySites,
]

const FILTER_LABELS = {
  [Filters.Periods]: "Période",
  [Filters.ProductionSites]: "Site de production",
  [Filters.MatieresPremieres]: "Matière Première",
  [Filters.Biocarburants]: "Biocarburant",
  [Filters.CountriesOfOrigin]: "Pays d'origine",
  [Filters.DeliverySites]: "Sites de livraison",
  [Filters.Clients]: "Clients",
  [Filters.Vendors]: "Fournisseurs",
}

export function mapFilters(
  filters: Snapshot["filters"],
  selected: FilterSelection["selected"]
): [Filters, string, SelectValue, Option[]][] {
  const filterList = Object.entries(filters)

  filterList.sort(
    (a, b) =>
      FILTER_ORDER.indexOf(a[0] as Filters) -
      FILTER_ORDER.indexOf(b[0] as Filters)
  )

  return filterList.map(([key, options]) => {
    const filter = key as Filters
    const value = selected[filter] ?? null
    return [filter, FILTER_LABELS[filter], value, options ?? []]
  })
}

type TransactionFiltersProps = {
  selection: FilterSelection
  search: SearchSelection
  filters: Snapshot["filters"]
}

const TransactionFilters = ({
  search,
  selection,
  filters,
}: TransactionFiltersProps) => (
  <div className={styles.transactionFilters}>
    <div className={styles.filterGroup}>
      {mapFilters(filters, selection.selected).map(
        ([filter, label, selected, options]) => (
          <Select
            clear
            search
            multiple
            key={filter}
            value={selected}
            placeholder={label}
            options={options}
            onChange={(value) => selection.select(filter, value)}
          />
        )
      )}
    </div>

    <SearchInput
      className={styles.searchInput}
      placeholder="Rechercher un lot"
      onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
        search.setQuery(e.target.value)
      }
    />
  </div>
)

export default TransactionFilters
