import React from "react"

import { TransactionFormState } from "../../hooks/helpers/use-transaction-form"
import { FormFields } from "../../hooks/helpers/use-form"
import { EntitySelection } from "../../hooks/helpers/use-entity"

import styles from "./transaction-form.module.css"

import {
  findBiocarburants,
  findCountries,
  findEntities,
  findMatieresPremieres,
  findProducers,
  findProductionSites,
  findDeliverySites,
} from "../../services/common"

import { Box, LabelCheckbox, LabelInput, LabelTextArea } from "../system"
import { Alert } from "../system/alert"
import AutoComplete from "../system/autocomplete"

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
  id?: string
  entity: EntitySelection
  readOnly?: boolean
  transaction: TransactionFormState
  error: string | null
  fieldErrors?: { [k: string]: string }
  onChange: <T extends FormFields>(e: React.ChangeEvent<T>) => void
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
}

const TransactionForm = ({
  id,
  entity,
  readOnly = false,
  transaction: tx,
  error,
  fieldErrors = {},
  onChange,
  onSubmit,
}: TransactionFormProps) => {
  const isProducer = entity?.entity_type === "Producteur"
  const isOperator = entity?.entity_type === "Opérateur"
  const isTrader = entity?.entity_type === "Trader"

  function submit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault()
    onSubmit && onSubmit(e)
  }

  return (
    <form id={id} className={styles.transactionForm} onSubmit={submit}>
      <Box row className={styles.transactionFields}>
        <Box>
          <LabelCheckbox
            disabled={readOnly || !entity?.has_mac}
            name="mac"
            label="Il s'agit d'une mise à consommation ?"
            checked={tx.mac}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Numéro douanier (DAE, DAA...)"
            name="dae"
            value={tx.dae}
            error={fieldErrors.dae}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            type="number"
            label="Volume à 20°C en Litres"
            name="volume"
            value={tx.volume}
            error={fieldErrors.volume}
            onChange={onChange}
          />
          <AutoComplete
            readOnly={readOnly}
            label="Biocarburant"
            placeholder="Rechercher un biocarburant..."
            name="biocarburant"
            value={tx.biocarburant}
            error={fieldErrors.biocarburant}
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
            error={fieldErrors.matiere_premiere}
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
            error={fieldErrors.pays_origine}
            getValue={getters.code_pays}
            getLabel={getters.name}
            getQuery={findCountries}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            type="date"
            label="Date de livraison"
            name="delivery_date"
            value={tx.delivery_date}
            error={fieldErrors.delivery_date}
            onChange={onChange}
          />
        </Box>
        <Box>
          <LabelCheckbox
            disabled={readOnly || isProducer || isTrader || isOperator}
            name="producer_is_in_carbure"
            label="Producteur enregistré sur Carbure ?"
            checked={tx.producer_is_in_carbure}
            onChange={onChange}
          />

          {tx.producer_is_in_carbure ? (
            <React.Fragment>
              <AutoComplete
                readOnly={readOnly || isProducer}
                label="Producteur"
                placeholder="Rechercher un producteur..."
                name="carbure_producer"
                value={tx.carbure_producer}
                error={fieldErrors.carbure_producer}
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
                error={fieldErrors.production_site}
                getValue={getters.id}
                getLabel={getters.name}
                getQuery={findProductionSites}
                queryArgs={[tx.carbure_producer?.id]}
                onChange={onChange}
              />
              <LabelInput
                disabled
                label="Pays de production"
                defaultValue={tx.carbure_production_site?.country?.name}
              />
              <LabelInput
                disabled
                type="date"
                label="Date de mise en service"
                defaultValue={tx.carbure_production_site?.date_mise_en_service}
              />
              <LabelInput disabled label="N° d'enregistrement double-compte" />
              <LabelInput disabled label="Référence Système Fournisseur" />
            </React.Fragment>
          ) : (
            <React.Fragment>
              <LabelInput
                readOnly={readOnly}
                label="Producteur"
                name="unknown_producer"
                value={tx.unknown_producer}
                error={fieldErrors.producer}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                label="Site de production"
                name="unknown_production_site"
                value={tx.unknown_production_site}
                error={fieldErrors.production_site}
                onChange={onChange}
              />
              <AutoComplete
                disabled={tx.producer_is_in_carbure}
                readOnly={readOnly}
                label="Pays de production"
                placeholder="Rechercher un pays..."
                name="unknown_production_country"
                value={tx.unknown_production_country}
                error={fieldErrors.unknown_production_country}
                getValue={getters.code_pays}
                getLabel={getters.name}
                getQuery={findCountries}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                disabled={tx.producer_is_in_carbure}
                type="date"
                label="Date de mise en service"
                name="unknown_production_site_com_date"
                value={tx.unknown_production_site_com_date}
                error={fieldErrors.production_site_com_date}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                disabled={tx.producer_is_in_carbure}
                label="N° d'enregistrement double-compte"
                name="unknown_production_site_dbl_counting"
                value={tx.unknown_production_site_dbl_counting}
                error={fieldErrors.production_site_dbl_counting}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                disabled={tx.producer_is_in_carbure}
                label="Référence Système Fournisseur"
                name="unknown_production_site_reference"
                value={tx.unknown_production_site_reference}
                error={fieldErrors.production_site_reference}
                onChange={onChange}
              />
            </React.Fragment>
          )}
        </Box>

        <Box className={styles.middleColumn}>
          <LabelCheckbox
            disabled={readOnly || isOperator}
            name="client_is_in_carbure"
            label="Client enregistré sur Carbure ?"
            checked={tx.client_is_in_carbure}
            onChange={onChange}
          />

          {tx.client_is_in_carbure ? (
            <AutoComplete
              readOnly={readOnly || isOperator}
              label="Client"
              placeholder="Rechercher un client..."
              name="carbure_client"
              value={tx.carbure_client}
              error={fieldErrors.client}
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
              error={fieldErrors.client}
              onChange={onChange}
            />
          )}

          <LabelCheckbox
            disabled={readOnly}
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
              error={fieldErrors.carbure_delivery_site_name}
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
                error={fieldErrors.delivery_site}
                onChange={onChange}
              />
            </React.Fragment>
          )}

          {tx.delivery_site_is_in_carbure ? (
            <LabelInput
              disabled
              label="Pays de livraison"
              defaultValue={tx.carbure_delivery_site?.country?.name}
            />
          ) : (
            <AutoComplete
              disabled={tx.delivery_site_is_in_carbure}
              readOnly={readOnly}
              label="Pays de livraison"
              name="unknown_delivery_site_country"
              value={tx.unknown_delivery_site_country}
              error={fieldErrors.delivery_site_country}
              getValue={getters.code_pays}
              getLabel={getters.name}
              getQuery={findCountries}
              onChange={onChange}
            />
          )}

          <LabelTextArea
            readOnly={readOnly}
            label="Champ Libre"
            name="champ_libre"
            value={tx.champ_libre}
            error={fieldErrors.champ_libre}
            onChange={onChange}
          />
        </Box>

        <Box>
          <Box row className={styles.transactionGES}>
            <Box>
              <span className={styles.transactionGESHeader}>Émissions</span>
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EEC"
                name="eec"
                value={tx.eec}
                error={fieldErrors.eec}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EL"
                name="el"
                value={tx.el}
                error={fieldErrors.el}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EP"
                name="ep"
                value={tx.ep}
                error={fieldErrors.ep}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ETD"
                name="etd"
                value={tx.etd}
                error={fieldErrors.etd}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EU"
                name="eu"
                value={tx.eu}
                error={fieldErrors.eu}
                step={0.1}
                className={styles.transactionTotal}
                onChange={onChange}
              />
            </Box>

            <Box>
              <span className={styles.transactionGESHeader}>Réductions</span>
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ESCA"
                name="esca"
                value={tx.esca}
                error={fieldErrors.esca}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ECCS"
                name="eccs"
                value={tx.eccs}
                error={fieldErrors.eccs}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="ECCR"
                name="eccr"
                value={tx.eccr}
                error={fieldErrors.eccr}
                step={0.1}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                type="number"
                label="EEE"
                name="eee"
                value={tx.eee}
                error={fieldErrors.eee}
                step={0.1}
                onChange={onChange}
              />
            </Box>
          </Box>
          <Box row className={styles.transactionGES}>
            <LabelInput
              readOnly
              label="Total"
              value={`${tx.ghg_total} gCO2eq/MJ`}
            />
            <LabelInput
              readOnly
              label="Réduction"
              value={`${tx.ghg_reduction}%`}
            />
          </Box>
        </Box>
      </Box>

      {error && (
        <Alert level="error" className={styles.transactionError}>
          {error}
        </Alert>
      )}
    </form>
  )
}

export default TransactionForm
