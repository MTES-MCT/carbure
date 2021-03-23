import React from "react"
import { LotForwarder } from "transactions/hooks/actions/use-forward-lots";
import { PromptFormProps } from "common/components/dialog";
import { Entity, Transaction } from "common/types";

import styles from "./forward.module.css"
import { Box } from "common/components";
import { EntityDeliverySite } from "settings/hooks/use-delivery-sites";
import { Button } from "common/components/button";
import Table, { Column } from "common/components/table";
import { DialogButtons } from 'common/components/dialog';
import { TransactionSelection } from "transactions/hooks/query/use-selection";

import * as C from "transactions/components/list-columns"

const COLUMNS: Column<EntityDeliverySite>[] = [
  C.padding,
  {
    header: 'Depot',
    render: (depot) => depot.depot?.name
  },
  {
    header: 'Incorporateur',
    render: (depot) => depot.blender?.name
  },
  C.padding,
]

export const OperatorForwardPromptFactory = (forwarder: LotForwarder, outsourceddepots: EntityDeliverySite[] | undefined) =>
 function OperatorForwardPrompt({
    onConfirm,
    onCancel,
  }: PromptFormProps<boolean>) {
    const rows = outsourceddepots?.map(od => ({ value: od })) ?? []

    return (
      <Box className={styles.importExplanation}>
        Voici vers quels opérateurs les lots seront transférés:

        <Table 
          columns={COLUMNS}
          rows={rows}
        />

        <DialogButtons>
          <Button level="primary" onClick={() => onConfirm(true)}>Transférer</Button>
          <Button onClick={onCancel}>Annuler</Button>  
        </DialogButtons>
      </Box>
    )
}


const TX_TO_TRANSFER_COLUMNS: Column<Transaction>[] = [
  C.padding,
  C.dae,
  C.matierePremiere,
  C.biocarburant,
  C.volume,
  C.deliverySite,
  C.padding
]

export const OperatorTransactionsToForwardPromptFactory = (s: TransactionSelection, outsourceddepots?: EntityDeliverySite[]) =>
 function OperatorForwardPrompt({
    onConfirm,
    onCancel,
  }: PromptFormProps<Transaction[]>) {
    const outsourceddepotsids = outsourceddepots?.map(d => (d.depot?.depot_id))
    const txs = s.getTransactions()
      .filter(t => (outsourceddepotsids?.includes(t.carbure_delivery_site?.depot_id)))
    const rows = txs.map(t => ({value: t}))

    return (
      <Box className={styles.importExplanation}>
        Voici les lots qui seront transférés:

        <Table 
          columns={TX_TO_TRANSFER_COLUMNS}
          rows={rows}
        />

        <DialogButtons>
          <Button level="primary" onClick={() => onConfirm(txs)}>Transférer</Button>
          <Button onClick={onCancel}>Annuler</Button>  
        </DialogButtons>
      </Box>
    )
}
