import React from "react"
import { Redirect } from "react-router-dom"

import { AsyncButton, Button, Title } from "../components/system"
import Modal from "../components/system/modal"
import TransactionForm from "../components/transaction-form"
import { Cross, Plus } from "../components/system/icons"
import { EntitySelection } from "../hooks/use-app"
import useTransactionAdd from "../hooks/use-transaction-add"

type TransactionAddProps = {
  entity: EntitySelection
  refresh: () => void
}

const TransactionAdd = ({ entity, refresh }: TransactionAddProps) => {
  const { form, request, change, submit, close } = useTransactionAdd(
    entity,
    refresh
  )

  if (entity.selected === null) {
    return <Redirect to="/transactions" />
  }

  return (
    <Modal onClose={close}>
      <Title>Créer un nouveau lot</Title>

      <TransactionForm
        transaction={form!}
        error={request.error}
        onChange={change}
        onSubmit={submit}
      >
        <AsyncButton
          submit
          kind="primary"
          icon={Plus}
          loading={request.loading}
        >
          Créer lot
        </AsyncButton>
        <Button icon={Cross} onClick={close}>
          Annuler
        </Button>
      </TransactionForm>
    </Modal>
  )
}

export default TransactionAdd
