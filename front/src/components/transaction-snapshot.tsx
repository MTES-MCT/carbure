import React from "react"

import { ApiState } from "../hooks/helpers/use-api"
import { Filters, LotStatus, Snapshot } from "../services/types"
import { StatusSelection, FilterSelection, SearchSelection, YearSelection } from "../hooks/use-transactions" // prettier-ignore

import styles from "./transaction-snapshot.module.css"

import { Title, StatusButton, SearchInput, Box } from "./system"
import Select from "./system/select"

const STATUS = [
  { key: LotStatus.Draft, label: "Brouillons" },
  { key: LotStatus.Validated, label: "Lots envoyés" },
  { key: LotStatus.ToFix, label: "Lots à corriger" },
  { key: LotStatus.Accepted, label: "Lots acceptés" },
]

const FILTERS = [
  { key: Filters.Periods, label: "Période" },
  { key: Filters.ProductionSites, label: "Site de production" },
  { key: Filters.MatieresPremieres, label: "Matière Première" },
  { key: Filters.Biocarburants, label: "Biocarburant" },
  { key: Filters.CountriesOfOrigin, label: "Pays d'origine" },
  { key: Filters.Clients, label: "Client" },
]

type TransactionSnapshotProps = {
  snapshot: ApiState<Snapshot>
  status: StatusSelection
  filters: FilterSelection
  year: YearSelection
  search: SearchSelection
}

const TransactionSnapshot = ({
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
        {STATUS.map(({ key, label }) => (
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
        {FILTERS.map(({ key, label }) => (
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
