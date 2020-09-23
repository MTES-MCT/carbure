import React from "react"
import cl from "clsx"

import styles from "./transaction-list.module.css"

import { getStatus, Lot, LotStatus } from "../services/lots"
import { Table } from "./system"
import { truncate } from "../utils/format"

type TransactionListProps = {
  transactions: Lot[]
}

const COLUMNS = [
  "Statut",
  "Date d'ajout",
  "N° Douane",
  "Client",
  "Biocarburant",
  "Provenance",
  "Destination",
  "Mat. Première",
  "Économie",
]

const STATUS = {
  [LotStatus.Draft]: "Brouillon",
  [LotStatus.Validated]: "Envoyé",
  [LotStatus.ToFix]: "À corriger",
  [LotStatus.Accepted]: "Accepté",
  [LotStatus.Weird]: "Problème",
}

const Cell = ({ text }: { text: string }) => (
  <span title={text}>{truncate(text)}</span>
)

const DualCell = ({ top, bottom }: { top: string; bottom: string }) => (
  <div className={styles.dualRow}>
    <Cell text={top} />
    <span title={bottom} className={styles.extraInfo}>
      {truncate(bottom, 40)}
    </span>
  </div>
)

const Status = ({ value }: { value: LotStatus }) => (
  <span
    className={cl(styles.status, {
      [styles.statusValidated]: value === LotStatus.Validated,
      [styles.statusToFix]: value === LotStatus.ToFix,
      [styles.statusAccepted]: value === LotStatus.Accepted,
    })}
  >
    {STATUS[value]}
  </span>
)

const TransactionList = ({ transactions }: TransactionListProps) => (
  <Table columns={COLUMNS} rows={transactions}>
    {(transaction) => (
      <tr key={transaction.lot.id} className={styles.row}>
        <td>
          <input type="checkbox" name={transaction.dae} />
        </td>

        <td>
          <Status value={getStatus(transaction)} />
        </td>

        <td>
          <Cell text={transaction.lot.period} />
        </td>

        <td>
          <Cell text={transaction.dae} />
        </td>

        <td>
          <Cell
            text={
              transaction.carbure_client?.name ?? transaction.unknown_client
            }
          />
        </td>

        <td>
          <DualCell
            top={transaction.lot.biocarburant.name}
            bottom={`${transaction.lot.volume}L`}
          />
        </td>

        <td>
          <DualCell
            top={
              transaction.lot.carbure_producer?.name ??
              transaction.lot.unknown_producer
            }
            bottom={
              transaction.lot.carbure_production_site?.country.name ??
              transaction.lot.unknown_production_country
            }
          />
        </td>

        <td>
          <DualCell
            top={
              transaction.carbure_delivery_site?.city ??
              transaction.unknown_delivery_site
            }
            bottom={
              transaction.carbure_delivery_site?.country.name ??
              transaction.unknown_delivery_site_country?.name
            }
          />
        </td>

        <td>
          <DualCell
            top={transaction.lot.matiere_premiere.name}
            bottom={transaction.lot.pays_origine.name}
          />
        </td>

        <td>
          <Cell text={`${transaction.lot.ghg_reduction}%`} />
        </td>

        <td>{">"}</td>
      </tr>
    )}
  </Table>
)

export default TransactionList
