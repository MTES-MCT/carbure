import React from "react"

import { AsyncButton, Button, Title } from "../components/system"
import Modal from "../components/system/modal"
import TransactionForm from "../components/transaction-form"
import { Cross, Plus } from "../components/system/icons"
import { EntitySelection } from "../hooks/helpers/use-entity"
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

  return (
    <Modal onClose={close}>
      <Title>Créer un nouveau lot</Title>

      <TransactionForm
        transaction={form}
        error={request.error}
        onChange={change}
        onSubmit={submit}
      >
        <AsyncButton
          submit
          level="primary"
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
