import React from "react"

import {
  TransactionDetailsHook,
  TransactionFormState,
} from "../hooks/use-transaction-details"

import styles from "./transaction-form.module.css"

import { Box, LabelCheckbox, LabelInput, LabelTextArea } from "./system"

type TransactionFormProps = {
  readOnly?: boolean
  transaction: TransactionFormState
  onChange?: TransactionDetailsHook[1]
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
  children: React.ReactNode
}

const TransactionForm = ({
  children,
  readOnly = false,
  transaction: tr,
  onChange,
  onSubmit,
}: TransactionFormProps) => {
  return (
    <form className={styles.transactionForm} onSubmit={onSubmit}>
      <div className={styles.transactionFields}>
        <Box>
          <LabelInput
            readOnly={readOnly}
            label="Producteur"
            name="producer"
            value={tr.producer}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Site de production"
            name="production_site"
            value={tr.production_site}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Volume à 20°C en Litres"
            name="volume"
            value={tr.volume}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Biocarburant"
            name="biocarburant_code"
            value={tr.biocarburant_code}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Matiere Premiere"
            name="matiere_premiere_code"
            value={tr.matiere_premiere_code}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Pays d'origine"
            name="pays_origine_code"
            value={tr.pays_origine_code}
            onChange={onChange}
          />
        </Box>

        <Box className={styles.middleColumn}>
          <LabelInput
            readOnly={readOnly}
            label="Numéro douanier (DAE, DAA...)"
            name="dae"
            value={tr.dae}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Client"
            name="client"
            value={tr.client}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Site de livraison"
            name="delivery_site"
            value={tr.delivery_site}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            type="date"
            label="Date de livraison"
            name="delivery_date"
            value={tr.delivery_date}
            onChange={onChange}
          />
          <LabelTextArea
            label="Champ Libre"
            name="champ_libre"
            value={tr.champ_libre}
            onChange={onChange}
          />
        </Box>

        <Box>
          <div className={styles.transactionGES}>
            <Box>
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EEC"
                name="eec"
                value={tr.eec}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EL"
                name="el"
                value={tr.el}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EP"
                name="ep"
                value={tr.ep}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ETD"
                name="etd"
                value={tr.etd}
                step={0.1}
                onChange={onChange}
              />
            </Box>

            <Box>
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ESCA"
                name="esca"
                value={tr.esca}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ECCS"
                name="eccs"
                value={tr.eccs}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ECCR"
                name="eccr"
                value={tr.eccr}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EEE"
                name="eee"
                value={tr.eee}
                step={0.1}
                onChange={onChange}
              />
            </Box>
          </div>

          <LabelInput
            readOnly={readOnly}
            type="number"
            label="EU"
            name="eu"
            value={tr.eu}
            step={0.1}
            className={styles.transactionTotal}
            onChange={onChange}
          />

          <LabelCheckbox
            name="mac"
            label="Mise à consommation ?"
            checked={tr.mac}
            className={styles.transactionMAC}
            onChange={onChange}
          />
        </Box>
      </div>

      <div className={styles.transactionFormButtons}>{children}</div>
    </form>
  )
}

export default TransactionForm
