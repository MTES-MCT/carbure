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

const cells = [
  // period
  (tx: Transaction) => tx.lot.period,

  // dae
  (tx: Transaction) => tx.dae,

  // client
  (tx: Transaction) => tx.carbure_client?.name ?? tx.unknown_client ?? "",

  // biocarburant
  (tx: Transaction) => [tx.lot.biocarburant.name, tx.lot.volume.toString()],

  // matiere premiere
  (tx: Transaction) => [tx.lot.matiere_premiere.name, tx.lot.pays_origine.name],

  // production site
  (tx: Transaction) => [
    tx.lot.carbure_production_site?.name ?? tx.lot.unknown_production_site,
    tx.lot.carbure_production_site?.country.name ?? tx.lot.unknown_production_country, // prettier-ignore
  ],

  // delivery site
  (tx: Transaction) => {
    const name = tx.carbure_delivery_site?.name ?? tx.unknown_delivery_site
    const country = tx.carbure_delivery_site?.country.name ?? tx.unknown_delivery_site_country?.name // prettier-ignore
    const city = tx.carbure_delivery_site?.city // prettier-ignore

    return [name ?? "", city ? `${country}, ${city}` : country]
  },

  // ghg reduction
  (tx: Transaction) => `${tx.lot.ghg_reduction}%`,
]

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

const TwoLines = ({ text }: { text: string[] }) => (
  <div className={styles.dualRow}>
    <Line text={text[0]} />
    <Line small text={text[1]} />
  </div>
)

const TwoLines_old = ({ top, bottom }: { top: string; bottom: string }) => (
  <div className={styles.dualRow}>
    <Line text={top} />
    <Line small text={bottom} />
  </div>
)

function mapCells(getters: typeof cells, transaction: Transaction) {
  return getters.map((getter) => getter(transaction))
}

type TxRowProps = {
  transaction: Transaction
}

export const TransactionRow = ({ transaction }: TxRowProps) => (
  <React.Fragment>
    <td>
      <Status value={getStatus(transaction)} />
    </td>

    {mapCells(cells, transaction).map((value, i) => (
      <td key={i}>
        {Array.isArray(value) ? (
          <TwoLines text={value} />
        ) : (
          <Line text={value} />
        )}
      </td>
    ))}
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
      onClick={() => relativePush(`${id}`)}
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
      <TwoLines_old
        top={tx.lot.biocarburant.name}
        bottom={`${tx.lot.volume}L`}
      />
    </td>

    <td>
      <TwoLines_old
        top={tx.lot.carbure_producer?.name ?? tx.lot.unknown_producer}
        bottom={
          tx.lot.carbure_production_site?.country.name ??
          tx.lot.unknown_production_country
        }
      />
    </td>

    <td>
      <TwoLines_old
        top={tx.carbure_delivery_site?.city ?? tx.unknown_delivery_site ?? ""}
        bottom={
          tx.carbure_delivery_site?.country.name ??
          tx.unknown_delivery_site_country?.name
        }
      />
    </td>

    <td>
      <TwoLines_old
        top={tx.lot.matiere_premiere.name}
        bottom={tx.lot.pays_origine.name}
      />
    </td>

    <td>
      <Line text={`${tx.lot.ghg_reduction}%`} />
    </td>
  </React.Fragment>
)
