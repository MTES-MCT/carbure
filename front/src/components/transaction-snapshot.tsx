import React from "react"

import { ApiState } from "../hooks/helpers/use-api"
import { Filters, LotStatus, Snapshot } from "../services/types"
import { StatusSelection, FilterSelection, SearchSelection } from "../hooks/use-transactions" // prettier-ignore

import styles from "./transaction-snapshot.module.css"

import { Plus } from "./system/icons"
import { Title, Button, StatusButton, SearchInput, Box } from "./system"
import Select from "./system/select"
import { Link } from "./relative-route"

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
  search: SearchSelection
}

const TransactionSnapshot = ({
  snapshot,
  status,
  filters,
  search,
}: TransactionSnapshotProps) => (
  <Box className={styles.transactionSnapshot}>
    <div className={styles.transactionSummary}>
      <div className={styles.transactionHeader}>
        <Title>Transactions</Title>

        <Box row>
          <Link relative to="../draft/add">
            <Button level="primary">
              <Plus />
              Ajouter des lots
            </Button>
          </Link>
        </Box>
      </div>

      <div className={styles.transactionStatus}>
        {STATUS.map(({ key, label }) => (
          <Link key={key} relative to={`../${key}`}>
            <StatusButton
              active={key === status.active}
              amount={snapshot.loading ? "…" : snapshot.data?.lots[key] ?? 0}
              label={label}
            />
          </Link>
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
            onChange={(value) => filters.selectFilter(key, value)}
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
