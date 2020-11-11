import React from "react"
import { EntitySelection } from "../../hooks/helpers/use-entity"
import { SettingsGetter } from "../../hooks/use-app"

import styles from "./settings.module.css"

import * as api from "../../services/settings"
import useAPI from "../../hooks/helpers/use-api"

import { Title, LabelCheckbox, LoaderOverlay } from "../system"
import { SectionHeader, SectionBody, Section } from "../system/section"

export function toggleMAC(toggle: boolean, entityID: number) {
  return toggle ? api.enableMAC(entityID) : api.disableMAC(entityID)
}

export function toggleTrading(toggle: boolean, entityID: number) {
  return toggle ? api.enableTrading(entityID) : api.disableTrading(entityID)
}

type CompanySettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

const CompanySettings = ({ entity, settings }: CompanySettingsProps) => {
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
      <SectionHeader>
        <Title>Société</Title>
      </SectionHeader>

      <SectionBody>
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
      </SectionBody>

      {isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default CompanySettings
