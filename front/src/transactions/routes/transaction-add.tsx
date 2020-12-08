import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"

import styles from "../components/form.module.css"

import useTransactionAdd from "../hooks/use-transaction-add"
import Modal from "common/components/modal"
import { AsyncButton, Button } from "common/components/button"
import { Plus, Return } from "common/components/icons"
import { StatusTitle } from "../components/status"
import TransactionForm from "../components/form"

type TransactionAddProps = {
  entity: EntitySelection
  refresh: () => void
}

const TransactionAdd = ({ entity, refresh }: TransactionAddProps) => {
  const { form, request, change, submit, close } = useTransactionAdd(
    entity,
    refresh
  )

  return (
    <Modal onClose={close}>
      <StatusTitle editable>Créer une nouvelle transaction</StatusTitle>

      <TransactionForm
        id="transaction-add"
        entity={entity}
        transaction={form}
        error={request.error}
        onChange={change}
        onSubmit={submit}
      />

      <div className={styles.transactionFormButtons}>
        <AsyncButton
          submit="transaction-add"
          level="primary"
          icon={Plus}
          loading={request.loading}
        >
          Créer lot
        </AsyncButton>
        <Button
          icon={Return}
          className={styles.transactionCloseButton}
          onClick={close}
        >
          Retour
        </Button>
      </div>
    </Modal>
  )
}

export default TransactionAdd
