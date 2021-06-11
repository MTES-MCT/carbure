import { Trans, useTranslation } from "react-i18next"
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

type OperatorForwardPromptProps = PromptProps<boolean> & {
  outsourceddepots: EntityDeliverySite[] | undefined
}

export const OperatorForwardPrompt = ({
  outsourceddepots,
  onResolve,
}: OperatorForwardPromptProps) => {
  const { t } = useTranslation()
  const rows = outsourceddepots?.map((od) => ({ value: od })) ?? []

  const columns: Column<EntityDeliverySite>[] = [
    C.padding,
    {
      header: t("Depot"),
      render: (depot) => depot.depot?.name,
    },
    {
      header: t("Incorporateur"),
      render: (depot) => depot.blender?.name,
    },
    C.padding,
  ]

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={t("Transfert de lots")} />
      <DialogText
        text={t(
          "Vous pouvez transférer vos lots reçus dans un dépôt pour lequel l'incorporation peut être effectuée par une société tierce."
        )}
      />

      <Box className={styles.importExplanation}>
        <Trans>Voici vers quels opérateurs les lots seront transférés:</Trans>
      </Box>

      <Table columns={columns} rows={rows} className={styles.forwardTable} />

      <DialogButtons>
        <Button level="primary" onClick={() => onResolve(true)}>
          <Trans>Transférer</Trans>
        </Button>
        <Button onClick={() => onResolve(false)}>
          <Trans>Annuler</Trans>
        </Button>
      </DialogButtons>
    </Dialog>
  )
}

type OperatorTransactionsToForwardPromptProps = PromptProps<Transaction[]> & {
  selection: TransactionSelection
  outsourceddepots?: EntityDeliverySite[]
}

export const OperatorTransactionsToForwardPrompt = ({
  selection,
  outsourceddepots,
  onResolve,
}: OperatorTransactionsToForwardPromptProps) => {
  const { t } = useTranslation()
  const outsourceddepotsids = outsourceddepots?.map((d) => d.depot?.depot_id)
  const txs = selection
    .getTransactions()
    .filter((t) =>
      outsourceddepotsids?.includes(t.carbure_delivery_site?.depot_id)
    )

  const columns: Column<Transaction>[] = [
    C.padding,
    C.dae(t),
    C.matierePremiere(t),
    C.biocarburant(t),
    C.volume(t),
    C.deliverySite(t),
    C.padding,
  ]

  const rows = txs.map((t) => ({ value: t }))

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={t("Transférer lot")} />
      <DialogText text={t("Voulez vous transférer les lots sélectionnés ?")} />

      <Box className={styles.importExplanation}>
        <Trans>Voici les lots qui seront transférés:</Trans>
      </Box>

      <Table columns={columns} rows={rows} className={styles.forwardTable} />

      <DialogButtons>
        <Button level="primary" onClick={() => onResolve(txs)}>
          <Trans>Transférer</Trans>
        </Button>
        <Button onClick={() => onResolve()}>
          <Trans>Annuler</Trans>
        </Button>
      </DialogButtons>
    </Dialog>
  )
}
