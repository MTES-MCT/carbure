import { Trans, useTranslation } from "react-i18next"

import { EntityManager } from "carbure/hooks/entity"
import { CompanySettingsHook } from "../hooks/use-company"
import { UserRole } from "common/types"
import { Title, LoaderOverlay } from "common/components"
import { Label } from "common/components/input"
import { SectionHeader, SectionBody, Section } from "common/components/section"
import Select from "common/components/select"
import styles from "./settings.module.css"
import Checkbox from "common-v2/components/checkbox"

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
        <Checkbox
          disabled={!canModify}
          label={t("Ma société effectue des Mises à Consommation")}
          value={settings.hasMAC}
          onChange={settings.onChangeMAC}
          className={styles.settingsCheckbox}
        />

        {isProducer && (
          <Checkbox
            disabled={!canModify}
            label={t("Ma société a une activité de négoce")}
            value={settings.hasTrading || isTrader}
            onChange={settings.onChangeTrading}
            className={styles.settingsCheckbox}
          />
        )}

        {(isTrader || isProducer) && settings.certificates.length > 0 && (
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
