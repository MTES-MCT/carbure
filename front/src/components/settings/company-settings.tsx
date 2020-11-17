import React from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"
import { CompanySettingsHook } from "../../hooks/settings/use-company"

import styles from "./settings.module.css"

import { Title, LabelCheckbox, LoaderOverlay } from "../system"
import { SectionHeader, SectionBody, Section } from "../system/section"

type CompanySettingsProps = {
  entity: EntitySelection
  settings: CompanySettingsHook
}

const CompanySettings = ({ entity, settings }: CompanySettingsProps) => {
  const isOperator = entity?.entity_type === "Opérateur"
  const isTrader = entity?.entity_type === "Trader"

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
          checked={settings.hasMAC || isOperator}
          onChange={settings.onChangeMAC}
          className={styles.settingsCheckbox}
        />

        <LabelCheckbox
          disabled={isOperator || isTrader}
          label="Ma société a une activité de négoce"
          checked={settings.hasTrading || isTrader}
          onChange={settings.onChangeTrading}
          className={styles.settingsCheckbox}
        />
      </SectionBody>

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default CompanySettings
