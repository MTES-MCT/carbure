import React from "react"

import { EntitySelection } from "carbure/hooks/use-entity"
import { CompanySettingsHook } from "../hooks/use-company"

import styles from "./settings.module.css"

import { Title, LabelCheckbox, LoaderOverlay } from "common/components"
import { SectionHeader, SectionBody, Section } from "common/components/section"

type CompanySettingsProps = {
  entity: EntitySelection
  settings: CompanySettingsHook
}

const CompanySettings = ({ entity, settings }: CompanySettingsProps) => {
  if (entity === null) {
    return null
  }

  const isOperator = entity.entity_type === "Opérateur"
  const isTrader = entity.entity_type === "Trader"

  return (
    <Section>
      <SectionHeader>
        <Title>Options</Title>
      </SectionHeader>

      <SectionBody>
        <LabelCheckbox
          label="Ma société effectue des Mises à Consommation"
          checked={settings.hasMAC}
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
