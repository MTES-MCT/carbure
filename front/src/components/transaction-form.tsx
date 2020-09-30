import React from "react"

import {
  TransactionDetailsHook,
  TransactionFormState,
} from "../hooks/use-transaction-details"

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

import { Box, LabelCheckbox, LabelInput, LabelTextArea } from "./system"
import AutoComplete from "./system/autocomplete"

// shorthand to build autocomplete value & label getters
const get = (key: string) => (obj: { [k: string]: any } | null) =>
  obj && key in obj ? String(obj[key]) : ""

type TransactionFormProps = {
  readOnly?: boolean
  transaction: TransactionFormState
  children: React.ReactNode
  onChange: TransactionDetailsHook[1]
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
}

const TransactionForm = ({
  children,
  readOnly = false,
  transaction: tr,
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
            value={tr.volume}
            onChange={onChange}
          />
          <AutoComplete
            readOnly={readOnly}
            label="Biocarburant"
            placeholder="Rechercher un biocarburant..."
            name="biocarburant"
            value={tr.biocarburant}
            getValue={get("code")}
            getLabel={get("name")}
            getQuery={findBiocarburants}
            onChange={onChange}
          />
          <AutoComplete
            readOnly={readOnly}
            label="Matiere Premiere"
            placeholder="Rechercher une matière première..."
            name="matiere_premiere"
            value={tr.matiere_premiere}
            getValue={get("code")}
            getLabel={get("name")}
            getQuery={findMatieresPremieres}
            onChange={onChange}
          />
          <AutoComplete
            readOnly={readOnly}
            label="Pays d'origine"
            placeholder="Rechercher un pays..."
            name="pays_origine"
            value={tr.pays_origine}
            getValue={get("code_pays")}
            getLabel={get("name")}
            getQuery={findCountries}
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
          <LabelCheckbox
            name="producer_is_in_carbure"
            label="Producteur enregistré sur Carbure ?"
            checked={tr.producer_is_in_carbure}
            onChange={onChange}
          />

          {tr.producer_is_in_carbure ? (
            <React.Fragment>
              <AutoComplete
                readOnly={readOnly}
                label="Producteur"
                placeholder="Rechercher un producteur..."
                name="carbure_producer"
                value={tr.carbure_producer}
                getValue={get("id")}
                getLabel={get("name")}
                getQuery={findProducers}
                onChange={onChange}
              />

              <AutoComplete
                readOnly={readOnly}
                label="Site de production"
                placeholder="Rechercher un site de production..."
                name="carbure_production_site"
                value={tr.carbure_production_site}
                getValue={get("id")}
                getLabel={get("name")}
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
                value={tr.unknown_producer}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                label="Site de production"
                name="unknown_production_site"
                value={tr.unknown_production_site}
                onChange={onChange}
              />
            </React.Fragment>
          )}

          <AutoComplete
            disabled={tr.producer_is_in_carbure}
            readOnly={readOnly}
            label="Pays de production"
            placeholder="Rechercher un pays..."
            name="unknown_production_country"
            value={tr.unknown_production_country}
            getValue={get("code_pays")}
            getLabel={get("name")}
            getQuery={findCountries}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            disabled={tr.producer_is_in_carbure}
            label="N° d'enregistrement double-compte"
            name="unknown_production_site_dbl_counting"
            value={tr.unknown_production_site_dbl_counting}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            disabled={tr.producer_is_in_carbure}
            label="Référence Système Fournisseur"
            name="unknown_production_site_reference"
            value={tr.unknown_production_site_reference}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            disabled={tr.producer_is_in_carbure}
            label="Date de mise en service"
            name="unknown_production_site_com_date"
            value={tr.unknown_production_site_com_date}
            onChange={onChange}
          />
        </Box>

        <Box className={styles.middleColumn}>
          <LabelCheckbox
            name="client_is_in_carbure"
            label="Client enregistré sur Carbure ?"
            checked={tr.client_is_in_carbure}
            onChange={onChange}
          />

          {tr.client_is_in_carbure ? (
            <AutoComplete
              readOnly={readOnly}
              label="Client"
              placeholder="Rechercher un client..."
              name="carbure_client"
              value={tr.carbure_client}
              getValue={get("id")}
              getLabel={get("name")}
              getQuery={findEntities}
              onChange={onChange}
            />
          ) : (
            <LabelInput
              readOnly={readOnly}
              label="Client"
              name="unknown_client"
              value={tr.unknown_client}
              onChange={onChange}
            />
          )}

          <LabelCheckbox
            name="delivery_site_is_on_carbure"
            label="Site de livraison enregistré sur Carbure ?"
            checked={tr.delivery_site_is_on_carbure}
            onChange={onChange}
          />

          {tr.delivery_site_is_on_carbure ? (
            <AutoComplete
              readOnly={readOnly}
              label="Site de livraison"
              placeholder="Rechercher un site de livraison..."
              name="carbure_delivery_site"
              value={tr.carbure_delivery_site}
              getValue={get("depot_id")}
              getLabel={get("name")}
              getQuery={findDeliverySites}
              onChange={onChange}
            />
          ) : (
            <React.Fragment>
              <LabelInput
                readOnly={readOnly}
                label="Site de livraison"
                name="unknown_delivery_site"
                value={tr.unknown_delivery_site}
                onChange={onChange}
              />
            </React.Fragment>
          )}

          <AutoComplete
            disabled={tr.delivery_site_is_on_carbure}
            readOnly={readOnly}
            label="Pays de livraison"
            name="unknown_delivery_site_country"
            value={tr.unknown_delivery_site_country}
            getValue={get("code_pays")}
            getLabel={get("name")}
            getQuery={findCountries}
            onChange={onChange}
          />

          <LabelInput
            readOnly={readOnly}
            label="Numéro douanier (DAE, DAA...)"
            name="dae"
            value={tr.dae}
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
        </Box>

        <Box>
          <Box row className={styles.transactionGES}>
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
          </Box>

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
      </Box>

      <div className={styles.transactionFormButtons}>{children}</div>
    </form>
  )
}

export default TransactionForm
