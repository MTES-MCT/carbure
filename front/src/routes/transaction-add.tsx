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

// empty form state
const initialState: TransactionFormState = {
  id: 0,
  dae: "",
  volume: 0,
  champ_libre: "",
  delivery_date: "",
  mac: false,
  pays_origine: null,

  eec: 0,
  el: 0,
  ep: 0,
  etd: 0,
  eu: 0,
  esca: 0,
  eccs: 0,
  eccr: 0,
  eee: 0,

  biocarburant: null,
  matiere_premiere: null,

  producer_is_in_carbure: true,
  carbure_producer: null,
  unknown_producer: "",

  production_site_is_in_carbure: true,
  carbure_production_site: null,
  unknown_production_site: "",
  unknown_production_country: null,
  unknown_production_site_com_date: "",
  unknown_production_site_reference: "",
  unknown_production_site_dbl_counting: "",

  client_is_in_carbure: true,
  carbure_client: null,
  unknown_client: "",

  delivery_site_is_on_carbure: true,
  carbure_delivery_site: null,
  unknown_delivery_site: "",
  unknown_delivery_site_country: null,
}

type TransactionAddProps = {
  entity: EntitySelection
}

const TransactionAdd = ({ entity }: TransactionAddProps) => {
  const history = useHistory()
  const [addedLot, resolve] = useAPI()

  const [form, change] = useForm<TransactionFormState>(initialState)

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
