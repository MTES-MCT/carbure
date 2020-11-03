import React from "react"
import cl from "clsx"

import { Transaction } from "../services/types"
import styles from "./transaction-status.module.css"

function getStatusText(tx: Transaction): string {
  if (tx.lot.status === "Draft") {
    return "Brouillon"
  }

  switch (tx.delivery_status) {
    case "N":
      return "En attente"
    case "A":
      return "Accepté"
    case "R":
      return "Refusé"
    case "AC":
      return "À corriger"
    case "AA":
      return "Corrigé"
  }
}

function getStatusClass(tx: Transaction): string {
  if (tx.lot.status === "Draft") return ""

  switch (tx.delivery_status) {
    case "N":
      return styles.statusWaiting
    case "R":
      return styles.statusRejected
    case "AC":
      return styles.statusToFix
    case "A":
    case "AA":
      return styles.statusAccepted
  }
}

type StatusProps = {
  transaction: Transaction
}

const Status = ({ transaction }: StatusProps) => (
  <span className={cl(styles.status, getStatusClass(transaction))}>
    {getStatusText(transaction)}
  </span>
)

export default Status
