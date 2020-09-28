import React from "react"

import { ApiState } from "../hooks/use-api"
import { Filters, LotStatus, Snapshot } from "../services/types"
import { StatusSelection, FilterSelection } from "../hooks/use-transactions"

import styles from "./transaction-snapshot.module.css"

import { Plus } from "./icons"
import { Title, Button, StatusButton, SearchInput } from "./system"
import Select from "./dropdown/select"

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
}

const TransactionSnapshot = ({
  snapshot,
  status,
  filters,
}: TransactionSnapshotProps) => (
  <React.Fragment>
    <div className={styles.transactionSnapshot}>
      <div className={styles.topRow}>
        <Title>Transactions</Title>

        <Button type="primary">
          <Plus />
          Ajouter des lots
        </Button>
      </div>

      <div className={styles.buttonRow}>
        {STATUS.map(({ key, label }) => (
          <StatusButton
            key={key}
            active={key === status.active}
            amount={snapshot.data?.lots[key] ?? "…"}
            label={label}
            onClick={() => status.setActive(key)}
          />
        ))}
      </div>
    </div>

    <div className={styles.lastRow}>
      <div className={styles.filters}>
        {FILTERS.map(({ key, label }) => (
          <Select
            search
            multiple
            key={key}
            value={filters.selected[key]}
            placeholder={label}
            options={snapshot.data?.filters[key] ?? []}
            onChange={(value) => filters.selectFilter(key, value)}
          />
        ))}
      </div>

      <SearchInput
        className={styles.searchInput}
        placeholder="Rechercher un lot"
      />
    </div>
  </React.Fragment>
)

export default TransactionSnapshot
