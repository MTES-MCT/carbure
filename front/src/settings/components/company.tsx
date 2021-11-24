import { Trans, useTranslation } from "react-i18next"

import { EntityManager } from "carbure/hooks/entity"
import { CompanySettingsHook } from "../hooks/use-company"
import { UserRole } from "common/types"
import { Title, LoaderOverlay } from "common/components"
import { Label, LabelCheckbox } from "common/components/input"
import { SectionHeader, SectionBody, Section } from "common/components/section"
import Select from "common/components/select"
import styles from "./settings.module.css"

type CompanySettingsProps = {
  entity: EntityManager
  settings: CompanySettingsHook
}

const CompanySettings = ({ entity, settings }: CompanySettingsProps) => {
  const { t } = useTranslation()

  const canModify = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)
  const { isProducer, isTrader } = entity

  return (
    <Section id="options">
      <SectionHeader>
        <Title>
          <Trans>Options</Trans>
        </Title>
      </SectionHeader>

      <SectionBody>
        <LabelCheckbox
          disabled={!canModify}
          label={t("Ma société effectue des Mises à Consommation")}
          checked={settings.hasMAC}
          onChange={(e) => settings.onChangeMAC(e.target.checked)}
          className={styles.settingsCheckbox}
        />

        {isProducer && (
          <LabelCheckbox
            disabled={!canModify}
            label={t("Ma société a une activité de négoce")}
            checked={settings.hasTrading || isTrader}
            onChange={(e) => settings.onChangeTrading(e.target.checked)}
            className={styles.settingsCheckbox}
          />
        )}

        {settings.certificates.length > 0 && (
          <Label
            label={t("Certificat par défaut")}
            className={styles.settingsSelect}
          >
            <Select
              placeholder={t("Sélectionner un certificat")}
              value={entity.default_certificate}
              onChange={settings.onChangeDefaultCertificate}
              options={settings.certificates}
            />
          </Label>
        )}
      </SectionBody>

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default CompanySettings
