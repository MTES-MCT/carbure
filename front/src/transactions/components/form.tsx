import React from "react"

import { TransactionFormState } from "../hooks/use-transaction-form"
import { FormFields } from "common/hooks/use-form"
import { EntitySelection } from "carbure/hooks/use-entity"

import styles from "./form.module.css"

import {
  findBiocarburants,
  findCountries,
  findEntities,
  findMatieresPremieres,
  findProducers,
  findProductionSites,
  findDeliverySites,
} from "common/api"

import { Box } from "common/components"
import {
  LabelCheckbox,
  LabelInput,
  LabelTextArea,
} from "common/components/input"
import { Alert } from "common/components/alert"
import { LabelAutoComplete } from "common/components/autocomplete"
import { AlertTriangle } from "common/components/icons"
import { EntityType } from "common/types"

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
  stock?: boolean
  transaction: TransactionFormState
  error: string | null
  fieldErrors?: { [k: string]: string }
  onChange: <T extends FormFields>(e: React.ChangeEvent<T>) => void
  onSubmit?: (e: React.FormEvent<HTMLFormElement>) => void
}

const TransactionForm = ({
  id,
  entity,
  stock = false,
  readOnly = false,
  transaction: tx,
  error,
  fieldErrors = {},
  onChange,
  onSubmit,
}: TransactionFormProps) => {
  const isProducer = entity?.entity_type === EntityType.Producer
  const isOperator = entity?.entity_type === EntityType.Operator
  const isTrader = entity?.entity_type === EntityType.Trader
  const isAdmin = entity?.entity_type === EntityType.Administration

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
            label="Volume en litres (Ethanol à 20°, autres à 15°)"
            name="volume"
            value={tx.volume}
            error={fieldErrors.volume}
            onChange={onChange}
          />
          <LabelAutoComplete
            readOnly={readOnly}
            label="Biocarburant"
            placeholder="Rechercher un biocarburant..."
            name="biocarburant"
            value={tx.biocarburant}
            error={fieldErrors.biocarburant_code}
            getValue={getters.code}
            getLabel={getters.name}
            minLength={0}
            getQuery={findBiocarburants}
            onChange={onChange}
          />
          <LabelAutoComplete
            readOnly={readOnly}
            label="Matiere Premiere"
            placeholder="Rechercher une matière première..."
            name="matiere_premiere"
            value={tx.matiere_premiere}
            error={fieldErrors.matiere_premiere_code}
            getValue={getters.code}
            getLabel={getters.name}
            minLength={0}
            getQuery={findMatieresPremieres}
            onChange={onChange}
          />
          <LabelAutoComplete
            readOnly={readOnly}
            label="Pays d'origine"
            placeholder="Rechercher un pays..."
            name="pays_origine"
            value={tx.pays_origine}
            error={fieldErrors.pays_origine_code}
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
            disabled={readOnly || isTrader || isOperator}
            name="producer_is_in_carbure"
            label="Producteur enregistré sur Carbure ?"
            checked={tx.producer_is_in_carbure}
            onChange={onChange}
          />

          {tx.producer_is_in_carbure ? (
            <React.Fragment key="in_carbure">
              <LabelAutoComplete
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
              <LabelAutoComplete
                readOnly={readOnly}
                label="Site de production"
                placeholder="Rechercher un site de production..."
                name="carbure_production_site"
                value={tx.carbure_production_site}
                error={fieldErrors.carbure_production_site}
                getValue={getters.id}
                getLabel={getters.name}
                minLength={0}
                getQuery={findProductionSites}
                queryArgs={[tx.carbure_producer?.id]}
                onChange={onChange}
              />
              <LabelInput
                disabled
                readOnly={readOnly}
                name="carbure_production_site_country"
                label="Pays de production"
                value={tx.carbure_production_site?.country?.name ?? ""}
              />
              <LabelInput
                disabled
                readOnly={readOnly}
                name="carbure_production_site_date"
                type="date"
                label="Date de mise en service"
                value={tx.carbure_production_site?.date_mise_en_service ?? ""}
              />
              <LabelInput
                disabled
                readOnly={readOnly}
                name="carbure_production_site_dbl_counting"
                label="N° d'enregistrement double-compte"
                value={tx.matiere_premiere?.is_double_compte ? (tx.carbure_production_site?.dc_reference ?? "") : ""} // prettier-ignore
              />
              <LabelInput
                disabled
                readOnly={readOnly}
                name="carbure_production_site_reference"
                label="Référence Système Fournisseur"
                value={tx.unknown_production_site_reference}
              />
            </React.Fragment>
          ) : (
            <React.Fragment key="not_in_carbure">
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
              <LabelAutoComplete
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
                type="date"
                label="Date de mise en service"
                name="unknown_production_site_com_date"
                value={tx.unknown_production_site_com_date}
                error={fieldErrors.unknown_production_site_com_date}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                label="N° d'enregistrement double-compte"
                name="unknown_production_site_dbl_counting"
                value={tx.unknown_production_site_dbl_counting ?? ""}
                error={fieldErrors.production_site_dbl_counting}
                onChange={onChange}
              />
              <LabelInput
                readOnly={readOnly}
                label="Référence Système Fournisseur"
                name="unknown_production_site_reference"
                value={tx.unknown_production_site_reference}
                error={fieldErrors.unknown_production_site_reference}
                onChange={onChange}
              />
            </React.Fragment>
          )}
        </Box>

        <Box className={styles.middleColumn}>
          {(isOperator || isTrader || isAdmin || stock) && (
            <React.Fragment>
              <LabelCheckbox
                disabled
                name="vendor_is_in_carbure"
                label="Fournisseur enregistré sur Carbure ?"
                checked={tx.vendor_is_in_carbure}
                onChange={onChange}
              />

              {tx.vendor_is_in_carbure ? (
                <LabelAutoComplete
                  readOnly={readOnly}
                  label="Fournisseur"
                  placeholder="Rechercher un fournisseur..."
                  name="carbure_vendor"
                  value={tx.carbure_vendor}
                  error={fieldErrors.vendor}
                  getValue={getters.id}
                  getLabel={getters.name}
                  getQuery={findEntities}
                  onChange={onChange}
                />
              ) : (
                <LabelInput
                  readOnly={readOnly}
                  label="Fournisseur"
                  name="unknown_vendor"
                  value={tx.unknown_vendor}
                  error={fieldErrors.vendor}
                  onChange={onChange}
                />
              )}
            </React.Fragment>
          )}

          {!isOperator && (
            <React.Fragment>
              <LabelCheckbox
                disabled={readOnly}
                name="client_is_in_carbure"
                label="Client enregistré sur Carbure ?"
                checked={tx.client_is_in_carbure}
                onChange={onChange}
              />

              {tx.client_is_in_carbure ? (
                <LabelAutoComplete
                  readOnly={readOnly}
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
            </React.Fragment>
          )}

          <LabelCheckbox
            disabled={readOnly}
            name="delivery_site_is_in_carbure"
            label="Site de livraison enregistré sur Carbure ?"
            checked={tx.delivery_site_is_in_carbure}
            onChange={onChange}
          />

          {tx.delivery_site_is_in_carbure ? (
            <LabelAutoComplete
              readOnly={readOnly}
              label="Site de livraison"
              placeholder="Rechercher un site de livraison..."
              name="carbure_delivery_site"
              value={tx.carbure_delivery_site}
              error={fieldErrors.delivery_site}
              getValue={getters.depot_id}
              getLabel={getters.name}
              getQuery={findDeliverySites}
              onChange={onChange}
            />
          ) : (
            <LabelInput
              readOnly={readOnly}
              label="Site de livraison"
              name="unknown_delivery_site"
              value={tx.unknown_delivery_site}
              error={fieldErrors.delivery_site}
              onChange={onChange}
            />
          )}

          {tx.delivery_site_is_in_carbure ? (
            <LabelInput
              disabled
              readOnly={readOnly}
              label="Pays de livraison"
              name="carbure_delivery_site_country"
              value={tx.carbure_delivery_site?.country?.name ?? ""}
            />
          ) : (
            <LabelAutoComplete
              disabled={tx.delivery_site_is_in_carbure}
              readOnly={readOnly}
              label="Pays de livraison"
              name="unknown_delivery_site_country"
              value={tx.unknown_delivery_site_country}
              error={fieldErrors.unknown_delivery_site_country}
              getValue={getters.code_pays}
              getLabel={getters.name}
              getQuery={findCountries}
              onChange={onChange}
            />
          )}

          {!isAdmin && !isTrader && !stock && (
            <LabelTextArea
              readOnly={readOnly}
              label="Champ Libre"
              name="champ_libre"
              value={tx.champ_libre}
              error={fieldErrors.champ_libre}
              onChange={onChange}
            />
          )}
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
                tooltip="Émissions résultant de l'extraction ou de la culture des matières premières"
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
                tooltip="Émissions annualisées résultant de modifications des stocks de carbone dues à des changements dans l'affectation des sols"
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
                tooltip="Émissions résultant de la transformation"
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
                tooltip="Émissions résultant du transport et de la distribution"
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
                tooltip="Émissions résultant du carburant à l'usage"
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
                tooltip="Réductions d'émissions dues à l'accumulation du carbone dans les sols grâce à une meilleure gestion agricole"
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
                tooltip="Réductions d'émissions dues au piégeage et au stockage géologique du carbone"
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
                tooltip="Réductions d'émissions dues au piégeage et à la substitution du carbone"
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
                tooltip="Réductions d'émissions dues à la production excédentaire d'électricité dans le cadre de la cogénération"
                step={0.1}
                onChange={onChange}
              />
            </Box>
          </Box>
          <Box row className={styles.transactionGES}>
            <LabelInput
              readOnly
              label="Total"
              name="ghg_total"
              value={`${tx.ghg_total.toFixed(2)} gCO2eq/MJ`}
            />
            <LabelInput
              readOnly
              label="Réduction"
              name="ghg_reduction"
              value={`${tx.ghg_reduction.toFixed(2)}%`}
            />
          </Box>
        </Box>
      </Box>

      {error && (
        <Alert
          level="error"
          icon={AlertTriangle}
          className={styles.transactionError}
        >
          {error}
        </Alert>
      )}
    </form>
  )
}

export default TransactionForm
