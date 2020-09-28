import React from "react"
import { Redirect, useHistory } from "react-router-dom"

import { TransactionFormState } from "../hooks/use-transaction-details"

import { Button, Title } from "../components/system"
import Modal from "../components/system/modal"
import TransactionForm from "../components/transaction-form"
import { Save, Cross } from "../components/system/icons"
import useForm from "../hooks/use-form"
import { EntitySelection } from "../hooks/use-app"

type TransactionAddProps = {
  entity: EntitySelection
}

const TransactionAdd = ({ entity }: TransactionAddProps) => {
  const history = useHistory()

  const [transaction, change] = useForm<TransactionFormState>({
    id: -1,
    biocarburant_code: "",
    matiere_premiere_code: "",
    pays_origine_code: "",
    producer: "",
    production_site: "",
    production_site_country: "",
    production_site_reference: "",
    production_site_commissioning_date: "",
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

  return (
    <Modal onClose={close}>
      <Title>Créer un nouveau lot</Title>

      <TransactionForm transaction={transaction!} onChange={change} />

      <Modal.Buttons>
        <Button type="primary">
          <Save /> Créer lot
        </Button>
        <Button onClick={close}>
          <Cross /> Annuler
        </Button>
      </Modal.Buttons>
    </Modal>
  )
}

export default TransactionAdd
