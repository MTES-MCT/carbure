import React from "react"

import { LotStatus, Snapshot } from "../services/lots"
import { ApiState } from "../hooks/use-api"

import styles from "./transaction-snapshot.module.css"

import { Plus } from "./icons"
import { Title, Button, StatusButton, Select, SearchInput } from "./system"

const STATUS = [
  { key: LotStatus.Drafts, label: "Brouillons" },
  { key: LotStatus.Validated, label: "Lots envoyés" },
  { key: LotStatus.ToFix, label: "Lots à corriger" },
  { key: LotStatus.Accepted, label: "Lots acceptés" },
]

const FILTERS = [
  { key: "periods", label: "Période" },
  { key: "production_sites", label: "Site de production" },
  { key: "matieres_premieres", label: "Matière Première" },
  { key: "biocarburants", label: "Biocarburant" },
  { key: "countries_of_origin", label: "Pays d'origine" },
  { key: "clients", label: "Client" },
]

type TransactionSnapshotProps = {
  snapshot: ApiState<Snapshot>
  activeStatus: { [k: string]: boolean }
  toggleStatus: Function
}

const TransactionSnapshot = ({
  snapshot,
  activeStatus,
  toggleStatus,
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
            active={activeStatus[key]}
            amount={snapshot.data?.lots[key] ?? "N/A"}
            label={label}
            onClick={() => toggleStatus(key)}
          />
        ))}
      </div>
    </div>

    <div className={styles.lastRow}>
      <div className={styles.filters}>
        {FILTERS.map(({ key, label }) => (
          <Select>
            <option disabled selected>
              {label}
            </option>
            {snapshot.data?.filters[key as keyof Snapshot["filters"]].map(
              ({ key, label }) => (
                <option value={key}>{label}</option>
              )
            )}
          </Select>
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
