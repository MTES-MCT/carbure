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

const STATUS_LABEL = {
  [LotStatus.Draft]: { singular: "Brouillon", plural: "Brouillons" },
  [LotStatus.Validated]: { singular: "Lot envoyé", plural: "Lots envoyés" },
  [LotStatus.ToFix]: { singular: "Lot à corriger", plural: "Lots à corriger" },
  [LotStatus.Accepted]: { singular: "Lot accepté", plural: "Lots acceptés" },
  [LotStatus.Weird]: { singular: "Lot incohérent", plural: "Lots incohérents" },
  [LotStatus.Stock]: { singular: "Stock", plural: "Stocks" },
}

const FILTER_LABELS = {
  [Filters.Periods]: "Période",
  [Filters.ProductionSites]: "Site de production",
  [Filters.MatieresPremieres]: "Matière Première",
  [Filters.Biocarburants]: "Biocarburant",
  [Filters.CountriesOfOrigin]: "Pays d'origine",
  [Filters.DeliverySites]: "Sites de livraison",
  [Filters.Clients]: "Clients",
}

function mapStatus(
  statuses: Snapshot["lots"] | undefined
): [LotStatus, string, number][] {
  if (!statuses) return []

  return Object.entries(statuses).map(([key, amount = 0]) => {
    const status = key as LotStatus
    const labels = STATUS_LABEL[status]
    return [status, amount === 1 ? labels.singular : labels.plural, amount]
  })
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
  year: YearSelection
}

export const TransactionSnapshot = ({
  snapshot,
  status,
  year,
}: TransactionSnapshotProps) => (
  <div className={styles.transactionSnapshot}>
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
      {mapStatus(snapshot.data?.lots).map(([key, label, amount]) => (
        <StatusButton
          key={key}
          active={key === status.active}
          loading={snapshot.loading}
          amount={amount}
          label={label}
          onClick={() => status.setActive(key)}
        />
      ))}
    </div>
  </div>
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
