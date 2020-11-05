import React from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"

import styles from "../../components/transaction/transaction-form.module.css"

import useTransactionAdd from "../../hooks/use-transaction-add"
import Modal from "../../components/system/modal"
import { AsyncButton, Button } from "../../components/system"
import { Plus, Return } from "../../components/system/icons"
import { StatusTitle } from "../../components/transaction/transaction-status"
import TransactionForm from "../../components/transaction/transaction-form"

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
