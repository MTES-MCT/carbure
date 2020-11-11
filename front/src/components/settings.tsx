import React from "react"
import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/use-app"

import styles from "./settings.module.css"

import * as api from "../services/settings"
import useAPI from "../hooks/helpers/use-api"
import {
  Section,
  BoxProps,
  Title,
  LabelCheckbox,
  LoaderOverlay,
} from "./system"

function toggleMAC(toggle: boolean, entityID: number) {
  return toggle ? api.enableMAC(entityID) : api.disableMAC(entityID)
}

function toggleTrading(toggle: boolean, entityID: number) {
  return toggle ? api.enableTrading(entityID) : api.disableTrading(entityID)
}

export const SettingsHeader = (props: BoxProps) => (
  <div className={styles.settingsTop}>
    <div {...props} className={styles.settingsHeader} />
  </div>
)

export const SettingsBody = (props: BoxProps) => (
  <div {...props} className={styles.settingsBody} />
)

type GeneralSettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

export const CompanySettings = ({ entity, settings }: GeneralSettingsProps) => {
  const isOperator = entity?.entity_type === "Opérateur"
  const isTrader = entity?.entity_type === "Trader"

  const hasMAC: boolean = entity?.has_mac ?? false
  const hasTrading: boolean = entity?.has_trading ?? false

  const [requestMAC, resolveToggleMAC] = useAPI(toggleMAC)
  const [requestTrading, resolveToggleTrading] = useAPI(toggleTrading)

  const isLoading =
    settings.loading || requestMAC.loading || requestTrading.loading

  function onChangeMac(e: React.ChangeEvent<HTMLInputElement>): void {
    if (entity !== null) {
      resolveToggleMAC(e.target.checked, entity.id).then(settings.resolve)
    }
  }

  function onChangeTrading(e: React.ChangeEvent<HTMLInputElement>): void {
    if (entity !== null) {
      resolveToggleTrading(e.target.checked, entity.id).then(settings.resolve)
    }
  }

  if (entity === null) {
    return null
  }

  return (
    <Section>
      <Title>Société</Title>

      <LabelCheckbox
        disabled={isOperator}
        label="Ma société effectue des Mises à Consommation"
        checked={hasMAC || isOperator}
        onChange={onChangeMac}
        className={styles.settingsCheckbox}
      />

      <LabelCheckbox
        disabled={isOperator || isTrader}
        label="Ma société a une activité de négoce"
        checked={hasTrading || isTrader}
        onChange={onChangeTrading}
        className={styles.settingsCheckbox}
      />

      {isLoading && <LoaderOverlay />}
    </Section>
  )
}

type ISCCCertificateSettingsProps = {}

export const ISCCCertificateSettings = ({}: ISCCCertificateSettingsProps) => (
  <Section>
    <Title>Certificats ISCC</Title>
  </Section>
)

type BBSCertificateSettingsProps = {}

export const BBSCertificateSettings = ({}: BBSCertificateSettingsProps) => (
  <Section>
    <Title>Certificats 2BS</Title>
  </Section>
)

type ProductionSitesSettingsProps = {}

export const ProductionSitesSettings = ({}: ProductionSitesSettingsProps) => (
  <Section>
    <Title>Sites de Production</Title>
  </Section>
)

type DeliverySitesSettingsProps = {}

export const DeliverySitesSettings = ({}: DeliverySitesSettingsProps) => (
  <Section>
    <Title>Dépôts</Title>
  </Section>
)
