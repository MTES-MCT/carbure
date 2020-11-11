import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/helpers/use-get-settings"

import { Main, Title } from "../components/system"
import {
  SettingsHeader,
  SettingsBody,
  CompanySettings,
  ProductionSitesSettings,
  DeliverySitesSettings,
  ISCCCertificateSettings,
  BBSCertificateSettings,
} from "../components/settings"

type SettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

const Settings = ({ entity, settings }: SettingsProps) => {
  const isProducer = entity?.entity_type === "Producteur"

  return (
    <Main>
      <SettingsHeader>
        <Title>Paramètres</Title>
      </SettingsHeader>

      <SettingsBody>
        <CompanySettings entity={entity} settings={settings} />
        {entity?.has_trading && <ISCCCertificateSettings />}
        {entity?.has_trading && <BBSCertificateSettings />}
        {isProducer && <ProductionSitesSettings />}
        <DeliverySitesSettings />
      </SettingsBody>
    </Main>
  )
}
export default Settings
