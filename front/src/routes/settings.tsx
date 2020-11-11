import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/helpers/use-get-settings"

import { Main, Title } from "../components/system"
import { SettingsHeader, SettingsBody } from "../components/settings"
import DeliverySitesSettings from "../components/settings/delivery-site-settings"
import ProductionSitesSettings from "../components/settings/production-site-settings"
import BBSCertificateSettings from "../components/settings/2bs-certificates-settings"
import ISCCCertificateSettings from "../components/settings/iscc-certificates-settings"
import CompanySettings from "../components/settings/company-settings"

type SettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

const Settings = ({ entity, settings }: SettingsProps) => {
  const isProducer = entity?.entity_type === "Producteur"
  const hasTrading = entity?.has_trading ?? false

  return (
    <Main>
      <SettingsHeader>
        <Title>Paramètres {entity?.name}</Title>
      </SettingsHeader>

      <SettingsBody>
        <CompanySettings entity={entity} settings={settings} />
        {hasTrading && <ISCCCertificateSettings entity={entity} />}
        {hasTrading && <BBSCertificateSettings entity={entity} />}
        {isProducer && <ProductionSitesSettings entity={entity} />}
        <DeliverySitesSettings entity={entity} />
      </SettingsBody>
    </Main>
  )
}
export default Settings
