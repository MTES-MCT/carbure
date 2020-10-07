import React from "react"

import { TransactionFormState } from "../hooks/helpers/use-transaction-form"

import styles from "./transaction-form.module.css"

import {
  findBiocarburants,
  findCountries,
  findEntities,
  findMatieresPremieres,
  findProducers,
  findProductionSites,
  findDeliverySites,
} from "../services/common"

import { Alert, Box, LabelCheckbox, LabelInput, LabelTextArea } from "./system"
import AutoComplete from "./system/autocomplete"
import { FormFields } from "../hooks/helpers/use-form"

// shorthand to build autocomplete value & label getters
const get = (key: string) => (obj: { [k: string]: any } | null) =>
  obj && key in obj ? String(obj[key]) : ""

const getters = {
  code: get("code"),
  name: get("name"),
  code_pays: get("code_pays"),
  id: get("id"),
  depot_id: get("depot_id"),
}

type TransactionFormProps = {
  readOnly?: boolean
  transaction: TransactionFormState
  children: React.ReactNode
  error: string | null
  onChange: <T extends FormFields>(e: React.ChangeEvent<T>) => void
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
}

const TransactionForm = ({
  children,
  readOnly = false,
  transaction: tx,
  error,
  onChange,
  onSubmit,
}: TransactionFormProps) => {
  function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    onSubmit && onSubmit(e)
  }

  return (
    <form className={styles.transactionForm} onSubmit={submit}>
      <Box row className={styles.transactionFields}>
        <Box>
          <LabelInput
            readOnly={readOnly}
            type="number"
            label="Volume à 20°C en Litres"
            name="volume"
            value={tx.volume}
            onChange={onChange}
          />
          <AutoComplete
            readOnly={readOnly}
            label="Biocarburant"
            placeholder="Rechercher un biocarburant..."
            name="biocarburant"
            value={tx.biocarburant}
            getValue={getters.code}
            getLabel={getters.name}
            getQuery={findBiocarburants}
            onChange={onChange}
          />
          <AutoComplete
            readOnly={readOnly}
            label="Matiere Premiere"
            placeholder="Rechercher une matière première..."
            name="matiere_premiere"
            value={tx.matiere_premiere}
            getValue={getters.code}
            getLabel={getters.name}
            getQuery={findMatieresPremieres}
            onChange={onChange}
          />
          <AutoComplete
            readOnly={readOnly}
            label="Pays d'origine"
            placeholder="Rechercher un pays..."
            name="pays_origine"
            value={tx.pays_origine}
            getValue={getters.code_pays}
            getLabel={getters.name}
            getQuery={findCountries}
            onChange={onChange}
          />

          <LabelTextArea
            label="Champ Libre"
            name="champ_libre"
            value={tx.champ_libre}
            onChange={onChange}
          />
        </Box>
        <Box>
          <LabelCheckbox
            name="producer_is_in_carbure"
            label="Producteur enregistré sur Carbure ?"
            checked={tx.producer_is_in_carbure}
            onChange={onChange}
          />

          {tx.producer_is_in_carbure ? (
            <React.Fragment>
              <AutoComplete
                readOnly={readOnly}
                label="Producteur"
                placeholder="Rechercher un producteur..."
                name="carbure_producer"
                value={tx.carbure_producer}
                getValue={getters.id}
                getLabel={getters.name}
                getQuery={findProducers}
                onChange={onChange}
              />

              <AutoComplete
                readOnly={readOnly}
                label="Site de production"
                placeholder="Rechercher un site de production..."
                name="carbure_production_site"
                value={tx.carbure_production_site}
                getValue={getters.id}
                getLabel={getters.name}
                getQuery={findProductionSites}
                onChange={onChange}
              />
            </React.Fragment>
          ) : (
            <React.Fragment>
              <LabelInput
                readOnly={readOnly}
                label="Producteur"
                name="unknown_producer"
                value={tx.unknown_producer}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                label="Site de production"
                name="unknown_production_site"
                value={tx.unknown_production_site}
                onChange={onChange}
              />
            </React.Fragment>
          )}

          <AutoComplete
            disabled={tx.producer_is_in_carbure}
            readOnly={readOnly}
            label="Pays de production"
            placeholder="Rechercher un pays..."
            name="unknown_production_country"
            value={tx.unknown_production_country}
            getValue={getters.code_pays}
            getLabel={getters.name}
            getQuery={findCountries}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            disabled={tx.producer_is_in_carbure}
            label="N° d'enregistrement double-compte"
            name="unknown_production_site_dbl_counting"
            value={tx.unknown_production_site_dbl_counting}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            disabled={tx.producer_is_in_carbure}
            label="Référence Système Fournisseur"
            name="unknown_production_site_reference"
            value={tx.unknown_production_site_reference}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            disabled={tx.producer_is_in_carbure}
            type="date"
            label="Date de mise en service"
            name="unknown_production_site_com_date"
            value={tx.unknown_production_site_com_date}
            onChange={onChange}
          />
        </Box>

        <Box className={styles.middleColumn}>
          <LabelCheckbox
            name="client_is_in_carbure"
            label="Client enregistré sur Carbure ?"
            checked={tx.client_is_in_carbure}
            onChange={onChange}
          />

          {tx.client_is_in_carbure ? (
            <AutoComplete
              readOnly={readOnly}
              label="Client"
              placeholder="Rechercher un client..."
              name="carbure_client"
              value={tx.carbure_client}
              getValue={getters.id}
              getLabel={getters.name}
              getQuery={findEntities}
              onChange={onChange}
            />
          ) : (
            <LabelInput
              readOnly={readOnly}
              label="Client"
              name="unknown_client"
              value={tx.unknown_client}
              onChange={onChange}
            />
          )}

          <LabelCheckbox
            name="delivery_site_is_in_carbure"
            label="Site de livraison enregistré sur Carbure ?"
            checked={tx.delivery_site_is_in_carbure}
            onChange={onChange}
          />

          {tx.delivery_site_is_in_carbure ? (
            <AutoComplete
              readOnly={readOnly}
              label="Site de livraison"
              placeholder="Rechercher un site de livraison..."
              name="carbure_delivery_site"
              value={tx.carbure_delivery_site}
              getValue={getters.depot_id}
              getLabel={getters.name}
              getQuery={findDeliverySites}
              onChange={onChange}
            />
          ) : (
            <React.Fragment>
              <LabelInput
                readOnly={readOnly}
                label="Site de livraison"
                name="unknown_delivery_site"
                value={tx.unknown_delivery_site}
                onChange={onChange}
              />
            </React.Fragment>
          )}

          <AutoComplete
            disabled={tx.delivery_site_is_in_carbure}
            readOnly={readOnly}
            label="Pays de livraison"
            name="unknown_delivery_site_country"
            value={tx.unknown_delivery_site_country}
            getValue={getters.code_pays}
            getLabel={getters.name}
            getQuery={findCountries}
            onChange={onChange}
          />

          <LabelInput
            readOnly={readOnly}
            label="Numéro douanier (DAE, DAA...)"
            name="dae"
            value={tx.dae}
            onChange={onChange}
          />

          <LabelInput
            readOnly={readOnly}
            type="date"
            label="Date de livraison"
            name="delivery_date"
            value={tx.delivery_date}
            onChange={onChange}
          />
        </Box>

        <Box>
          <Box row className={styles.transactionGES}>
            <Box>
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EEC"
                name="eec"
                value={tx.eec}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EL"
                name="el"
                value={tx.el}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EP"
                name="ep"
                value={tx.ep}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ETD"
                name="etd"
                value={tx.etd}
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
                value={tx.esca}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ECCS"
                name="eccs"
                value={tx.eccs}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ECCR"
                name="eccr"
                value={tx.eccr}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EEE"
                name="eee"
                value={tx.eee}
                step={0.1}
                onChange={onChange}
              />
            </Box>
          </Box>

          <LabelInput
            readOnly={readOnly}
            type="number"
            label="EU"
            name="eu"
            value={tx.eu}
            step={0.1}
            className={styles.transactionTotal}
            onChange={onChange}
          />

          <LabelCheckbox
            name="mac"
            label="Mise à consommation ?"
            checked={tx.mac}
            className={styles.transactionMAC}
            onChange={onChange}
          />
        </Box>
      </Box>

      {error && (
        <Alert level="error" className={styles.transactionError}>
          {error}
        </Alert>
      )}

      <div className={styles.transactionFormButtons}>{children}</div>
    </form>
  )
}

export default TransactionForm
