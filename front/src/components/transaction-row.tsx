import React from "react"
import cl from "clsx"

import styles from "./transaction-row.module.css"

import { getStatus } from "../services/lots"
import { LotStatus, Transaction } from "../services/types"
import { useRelativePush } from "./relative-route"

const STATUS = {
  [LotStatus.Draft]: "Brouillon",
  [LotStatus.Validated]: "Envoyé",
  [LotStatus.ToFix]: "À corriger",
  [LotStatus.Accepted]: "Accepté",
  [LotStatus.Weird]: "Problème",
  [LotStatus.Stock]: "Stock",
}

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

const Line = ({ text, small = false }: { text: string; small?: boolean }) => (
  <span title={text} className={cl(styles.rowLine, small && styles.extraInfo)}>
    {text}
  </span>
)

const TwoLines = ({ top, bottom }: { top: string; bottom: string }) => (
  <div className={styles.dualRow}>
    <Line text={top} />
    <Line small text={bottom} />
  </div>
)

type TxRowProps = {
  transaction: Transaction
}

export const TransactionRow = ({ transaction: tx }: TxRowProps) => (
  <React.Fragment>
    <td>
      <Status value={getStatus(tx)} />
    </td>

    <td>
      <Line text={tx.lot.period} />
    </td>

    <td>
      <Line text={tx.dae} />
    </td>

    <td>
      <Line text={tx.carbure_client?.name ?? tx.unknown_client ?? ""} />
    </td>

    <td>
      <TwoLines top={tx.lot.biocarburant.name} bottom={`${tx.lot.volume}L`} />
    </td>

    <td>
      <TwoLines
        top={tx.lot.carbure_producer?.name ?? tx.lot.unknown_producer}
        bottom={
          tx.lot.carbure_production_site?.country.name ??
          tx.lot.unknown_production_country
        }
      />
    </td>

    <td>
      <TwoLines
        top={tx.carbure_delivery_site?.city ?? tx.unknown_delivery_site ?? ""}
        bottom={
          tx.carbure_delivery_site?.country.name ??
          tx.unknown_delivery_site_country?.name
        }
      />
    </td>

    <td>
      <TwoLines
        top={tx.lot.matiere_premiere.name}
        bottom={tx.lot.pays_origine.name}
      />
    </td>

    <td>
      <Line text={`${tx.lot.ghg_reduction}%`} />
    </td>
  </React.Fragment>
)

type TxContainerProps = {
  id: number
  error: boolean
  children: React.ReactNode
}

export const TransactionRowContainer = ({
  id,
  error,
  children,
}: TxContainerProps) => {
  const relativePush = useRelativePush()

  return (
    <tr
      className={cl(styles.transactionRow, error && styles.transactionRowError)}
      onClick={() => relativePush(`/${id}`)}
    >
      {children}
    </tr>
  )
}

export const StockTransactionRow = ({ transaction: tx }: TxRowProps) => (
  <React.Fragment>

    <td>
      <Line text={tx.lot.carbure_id} />
    </td>

    <td>
      <TwoLines top={tx.lot.biocarburant.name} bottom={`${tx.lot.volume}L`} />
    </td>

    <td>
      <TwoLines
        top={tx.lot.carbure_producer?.name ?? tx.lot.unknown_producer}
        bottom={
          tx.lot.carbure_production_site?.country.name ??
          tx.lot.unknown_production_country
        }
      />
    </td>

    <td>
      <TwoLines
        top={tx.carbure_delivery_site?.city ?? tx.unknown_delivery_site ?? ""}
        bottom={
          tx.carbure_delivery_site?.country.name ??
          tx.unknown_delivery_site_country?.name
        }
      />
    </td>

    <td>
      <TwoLines
        top={tx.lot.matiere_premiere.name}
        bottom={tx.lot.pays_origine.name}
      />
    </td>

    <td>
      <Line text={`${tx.lot.ghg_reduction}%`} />
    </td>
  </React.Fragment>
)