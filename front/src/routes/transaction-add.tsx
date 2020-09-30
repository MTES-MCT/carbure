import React from "react"
import { Redirect, useHistory } from "react-router-dom"

import useTransactionForm, {
  toTransactionPostData,
} from "../hooks/helpers/use-transaction-form"
import useAPI from "../hooks/helpers/use-api"

import { AsyncButton, Button, Title } from "../components/system"
import Modal from "../components/system/modal"
import TransactionForm from "../components/transaction-form"
import { Save, Cross } from "../components/system/icons"
import { EntitySelection } from "../hooks/use-app"
import { addLots } from "../services/lots"

type TransactionAddProps = {
  entity: EntitySelection
}

const TransactionAdd = ({ entity }: TransactionAddProps) => {
  const history = useHistory()
  const [addedLot, resolve] = useAPI()

  const [form, change] = useTransactionForm()

  if (entity.selected === null) {
    return <Redirect to="/transactions" />
  }

  function close() {
    history.push("/transactions")
  }

  function submit() {
    if (entity.selected && form) {
      const params = {
        entity_id: entity.selected.id,
        ...toTransactionPostData(form),
      }

      resolve(addLots(params))
    }
  }

  return (
    <Modal onClose={close}>
      <Title>Créer un nouveau lot</Title>

      <TransactionForm transaction={form!} onChange={change} onSubmit={submit}>
        <AsyncButton
          submit
          kind="primary"
          icon={Save}
          loading={addedLot.loading}
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
