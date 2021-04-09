import {
  Dialog,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import { Transaction } from "common/types"

import styles from "./forward.module.css"
import { Box } from "common/components"
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites"
import { Button } from "common/components/button"
import Table, { Column } from "common/components/table"
import { DialogButtons } from "common/components/dialog"
import { TransactionSelection } from "transactions/hooks/query/use-selection"

import * as C from "transactions/components/list-columns"

const COLUMNS: Column<EntityDeliverySite>[] = [
  C.padding,
  {
    header: "Depot",
    render: (depot) => depot.depot?.name,
  },
  {
    header: "Incorporateur",
    render: (depot) => depot.blender?.name,
  },
  C.padding,
]

type OperatorForwardPromptProps = PromptProps<boolean> & {
  outsourceddepots: EntityDeliverySite[] | undefined
}

export const OperatorForwardPrompt = ({
  outsourceddepots,
  onResolve,
}: OperatorForwardPromptProps) => {
  const rows = outsourceddepots?.map((od) => ({ value: od })) ?? []

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text="Transfert de lots" />
      <DialogText text="Vous pouvez transférer vos lots reçus dans un dépôt pour lequel l'incorporation peut être effectuée par une société tierce." />

      <Box className={styles.importExplanation}>
        Voici vers quels opérateurs les lots seront transférés:
      </Box>

      <Table columns={COLUMNS} rows={rows} className={styles.forwardTable} />

      <DialogButtons>
        <Button level="primary" onClick={() => onResolve(true)}>
          Transférer
        </Button>
        <Button onClick={() => onResolve(false)}>Annuler</Button>
      </DialogButtons>
    </Dialog>
  )
}

const TX_TO_TRANSFER_COLUMNS: Column<Transaction>[] = [
  C.padding,
  C.dae,
  C.matierePremiere,
  C.biocarburant,
  C.volume,
  C.deliverySite,
  C.padding,
]

type OperatorTransactionsToForwardPromptProps = PromptProps<Transaction[]> & {
  selection: TransactionSelection
  outsourceddepots?: EntityDeliverySite[]
}

export const OperatorTransactionsToForwardPrompt = ({
  selection,
  outsourceddepots,
  onResolve,
}: OperatorTransactionsToForwardPromptProps) => {
  const outsourceddepotsids = outsourceddepots?.map((d) => d.depot?.depot_id)
  const txs = selection
    .getTransactions()
    .filter((t) =>
      outsourceddepotsids?.includes(t.carbure_delivery_site?.depot_id)
    )
  const rows = txs.map((t) => ({ value: t }))

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text="Transférer lot" />
      <DialogText text="Voulez vous transférer les lots sélectionnés ?" />

      <Box className={styles.importExplanation}>
        Voici les lots qui seront transférés:
      </Box>

      <Table
        columns={TX_TO_TRANSFER_COLUMNS}
        rows={rows}
        className={styles.forwardTable}
      />

      <DialogButtons>
        <Button level="primary" onClick={() => onResolve(txs)}>
          Transférer
        </Button>
        <Button onClick={() => onResolve()}>Annuler</Button>
      </DialogButtons>
    </Dialog>
  )
}
