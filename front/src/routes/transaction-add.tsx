import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"

import styles from "../components/transaction-form.module.css"

import useTransactionAdd from "../hooks/use-transaction-add"
import Modal from "../components/system/modal"
import { AsyncButton, Button, Title } from "../components/system"
import TransactionForm from "../components/transaction-form"
import { Plus, Return } from "../components/system/icons"

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
      <Title>Créer un nouveau lot</Title>

      <TransactionForm
        id="transaction-add"
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
