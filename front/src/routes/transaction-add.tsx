import React from "react"
import { Redirect, useHistory } from "react-router-dom"

import { TransactionFormState } from "../hooks/use-transaction-details"

import useAPI from "../hooks/use-api"
import useForm from "../hooks/use-form"

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

  const [form, change] = useForm<TransactionFormState>({
    id: -1,
    biocarburant_code: "",
    matiere_premiere_code: "",
    pays_origine_code: "",
    producer: "",
    production_site: "",
    production_site_country: "",
    production_site_reference: "",
    production_site_commissioning_date: "2020-09-21", // @TODO
    volume: 0,
    eec: 0,
    el: 0,
    ep: 0,
    etd: 0,
    eu: 0,
    esca: 0,
    eccs: 0,
    eccr: 0,
    eee: 0,
    dae: "",
    champ_libre: "",
    client: "",
    delivery_date: "",
    delivery_site: "",
    delivery_site_country: "",
    mac: false,
  })

  if (entity.selected === null) {
    return <Redirect to="/transactions" />
  }

  function close() {
    history.push("/transactions")
  }

  function submit() {
    if (entity.selected && form) {
      resolve(addLots(entity.selected.id, form))
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
