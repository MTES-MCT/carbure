import { Trans, useTranslation } from "react-i18next"

import { EntitySelection } from "carbure/hooks/use-entity"
import { CompanySettingsHook } from "../hooks/use-company"

import styles from "./settings.module.css"

import { Title, LoaderOverlay } from "common/components"
import { LabelCheckbox } from "common/components/input"
import { SectionHeader, SectionBody, Section } from "common/components/section"

type CompanySettingsProps = {
  entity: EntitySelection
  settings: CompanySettingsHook
}

const CompanySettings = ({ entity, settings }: CompanySettingsProps) => {
  const { t } = useTranslation()

  if (entity === null) {
    return null
  }

  const isOperator = entity.entity_type === "Opérateur"
  const isTrader = entity.entity_type === "Trader"

  return (
    <Section id="options">
      <SectionHeader>
        <Title>
          <Trans>Options</Trans>
        </Title>
      </SectionHeader>

      <SectionBody>
        <LabelCheckbox
          label={t("Ma société effectue des Mises à Consommation")}
          checked={settings.hasMAC}
          onChange={(e) => settings.onChangeMAC(e.target.checked)}
          className={styles.settingsCheckbox}
        />

        <LabelCheckbox
          disabled={isOperator || isTrader}
          label={t("Ma société a une activité de négoce")}
          checked={settings.hasTrading || isTrader}
          onChange={(e) => settings.onChangeTrading(e.target.checked)}
          className={styles.settingsCheckbox}
        />
      </SectionBody>

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default CompanySettings
