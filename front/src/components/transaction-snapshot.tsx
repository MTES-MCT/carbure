import React from "react"

import { ApiState } from "../hooks/helpers/use-api"
import { Filters, LotStatus, Snapshot, StockSnapshot } from "../services/types"
import { StatusSelection } from "../hooks/query/use-status"
import { YearSelection } from "../hooks/query/use-year"
import { FilterSelection } from "../hooks/query/use-filters"
import { SearchSelection } from "../hooks/query/use-search"

import styles from "./transaction-snapshot.module.css"

import { Title, StatusButton, SearchInput, Box } from "./system"
import Select, { SelectValue } from "./system/select"

const TRANSACTIONS_STATUS = [
  { key: LotStatus.Draft, label: "Brouillons" },
  { key: LotStatus.Validated, label: "Lots envoyés" },
  { key: LotStatus.ToFix, label: "Lots à corriger" },
  { key: LotStatus.Accepted, label: "Lots acceptés" },
]

const FILTER_LABELS = {
  [Filters.Periods]: "Période",
  [Filters.ProductionSites]: "Site de production",
  [Filters.MatieresPremieres]: "Matière Première",
  [Filters.Biocarburants]: "Biocarburant",
  [Filters.CountriesOfOrigin]: "Pays d'origine",
  [Filters.DeliverySites]: "Sites de livraison",
  [Filters.Clients]: "Clients",
}

function mapFilters(
  filters: FilterSelection["selected"]
): [Filters, string, SelectValue][] {
  return Object.entries(filters).map(([key, value]) => {
    const filter = key as Filters
    return [filter, FILTER_LABELS[filter], value ?? null]
  })
}

type TransactionSnapshotProps = {
  snapshot: ApiState<Snapshot>
  status: StatusSelection
  filters: FilterSelection
  year: YearSelection
  search: SearchSelection
}

export const TransactionSnapshot = ({
  snapshot,
  status,
  filters,
  year,
  search,
}: TransactionSnapshotProps) => (
  <Box className={styles.transactionSnapshot}>
    <div className={styles.transactionSummary}>
      <div className={styles.transactionHeader}>
        <Title>Transactions</Title>

        <Select
          level="primary"
          className={styles.transactionYear}
          value={year.selected}
          placeholder={snapshot.loading ? "…" : "Choisir une année"}
          options={snapshot.data?.years ?? []}
          onChange={(value) => year.setYear(value as number)}
        />
      </div>

      <div className={styles.transactionStatus}>
        {TRANSACTIONS_STATUS.map(({ key, label }) => (
          <StatusButton
            key={key}
            active={key === status.active}
            loading={snapshot.loading}
            amount={snapshot.data?.lots[key] ?? 0}
            label={label}
            onClick={() => status.setActive(key)}
          />
        ))}
      </div>
    </div>

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
            options={snapshot.data?.filters[filter] ?? []}
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
  </Box>
)

type StockSnapshotProps = {
  snapshot: ApiState<StockSnapshot>
  filters: FilterSelection
  search: SearchSelection
}

export const StocksSnapshot = ({
  snapshot,
  filters,
  search,
}: StockSnapshotProps) => (
  <Box className={styles.transactionSnapshot}>
    <div className={styles.transactionSummary}>
      <div className={styles.transactionHeader}>
        <Title>Stock</Title>
      </div>
    </div>

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
            options={snapshot.data?.filters[filter] ?? []}
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
  </Box>
)

export default TransactionSnapshot
