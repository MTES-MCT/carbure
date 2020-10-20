import React from "react"

import { Filters, Snapshot } from "../services/types"
import { FilterSelection } from "../hooks/query/use-filters"
import { SearchSelection } from "../hooks/query/use-search"

import styles from "./transaction-filters.module.css"

import { SearchInput } from "./system"
import Select, { SelectValue } from "./system/select"

const FILTER_LABELS = {
  [Filters.Periods]: "Période",
  [Filters.ProductionSites]: "Site de production",
  [Filters.MatieresPremieres]: "Matière Première",
  [Filters.Biocarburants]: "Biocarburant",
  [Filters.CountriesOfOrigin]: "Pays d'origine",
  [Filters.DeliverySites]: "Sites de livraison",
  [Filters.Clients]: "Clients",
}

export function mapFilters(
  filters: FilterSelection["selected"]
): [Filters, string, SelectValue][] {
  return Object.entries(filters).map(([key, value]) => {
    const filter = key as Filters
    return [filter, FILTER_LABELS[filter], value ?? null]
  })
}

type TransactionFiltersProps = {
  filters: FilterSelection
  search: SearchSelection
  options?: Snapshot["filters"]
}

const TransactionFilters = ({
  filters,
  search,
  options,
}: TransactionFiltersProps) => (
  <div className={styles.transactionFilters}>
    <div className={styles.filterGroup}>
      {mapFilters(filters.selected).map(([filter, label, value]) => (
        <Select
          clear
          search
          multiple
          key={filter}
          value={value}
          placeholder={label}
          options={(options && options[filter]) ?? []}
          onChange={(value) => filters.select(filter, value)}
        />
      ))}
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
