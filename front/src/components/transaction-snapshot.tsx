import React from "react"

import { ApiState } from "../hooks/helpers/use-api"
import { Filters, LotStatus, Snapshot, StockSnapshot } from "../services/types"
import { FilterSelection as FilterSelection_old, SearchSelection as SearchSelection_old } from "../hooks/use-transactions" // prettier-ignore
import { StatusSelection } from "../hooks/query/use-status"
import { YearSelection } from "../hooks/query/use-year"
import { FilterSelection } from "../hooks/query/use-filters"
import { SearchSelection } from "../hooks/query/use-search"

import styles from "./transaction-snapshot.module.css"

import { Title, StatusButton, SearchInput, Box } from "./system"
import Select from "./system/select"

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
  [Filters.Clients]: "Clients"
}

const STOCK_FILTERS = [
  { key: Filters.ProductionSites, label: "Site de production" },
  { key: Filters.MatieresPremieres, label: "Matière Première" },
  { key: Filters.Biocarburants, label: "Biocarburant" },
  { key: Filters.CountriesOfOrigin, label: "Pays d'origine" },
  { key: Filters.DeliverySites, label: "Sites de livraison" },
]

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
            amount={snapshot.loading ? "…" : snapshot.data?.lots[key] ?? 0}
            label={label}
            onClick={() => status.setActive(key)}
          />
        ))}
      </div>
    </div>

    <div className={styles.transactionFilters}>
      <div className={styles.filterGroup}>
        {Object.entries(filters.selected).map(([filter, value]) => (
          <Select
            clear
            search
            multiple
            key={filter}
            value={value}
            placeholder={snapshot.loading ? "…" : FILTER_LABELS[filter as Filters]}
            options={snapshot.data?.filters[filter as Filters] ?? []}
            onChange={(value) => filters.select(filter as Filters, value)}
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
  filters: FilterSelection_old
  search: SearchSelection_old
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
        {STOCK_FILTERS.map(({ key, label }) => (
          <Select
            clear
            search
            multiple
            key={key}
            value={filters.selected[key]}
            placeholder={snapshot.loading ? "…" : label}
            options={snapshot.data?.filters[key] ?? []}
            onChange={(value) => filters.select(key, value)}
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
