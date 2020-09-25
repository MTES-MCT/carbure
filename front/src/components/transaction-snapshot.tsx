import React from "react"

import { Filters, LotStatus, Snapshot } from "../services/lots"
import { ApiState } from "../hooks/use-api"

import styles from "./transaction-snapshot.module.css"

import { Plus } from "./icons"
import { Title, Button, StatusButton, SearchInput } from "./system"
import Select, { Option } from "./dropdown/select"

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
  activeStatus: string
  setActiveStatus: Function
  filters: { [k: string]: Option }
  setFilters: Function
}

const TransactionSnapshot = ({
  snapshot,
  activeStatus,
  setActiveStatus,
  filters,
  setFilters,
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
            active={key === activeStatus}
            amount={snapshot.data?.lots[key] ?? "…"}
            label={label}
            onClick={() => setActiveStatus(key)}
          />
        ))}
      </div>
    </div>

    <div className={styles.lastRow}>
      <div className={styles.filters}>
        {FILTERS.map(({ key, label }) => (
          <Select
            key={key}
            value={filters[key]}
            placeholder={label}
            options={snapshot.data?.filters[key] ?? []}
            onChange={(value) => setFilters({ ...filters, [key]: value })}
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
