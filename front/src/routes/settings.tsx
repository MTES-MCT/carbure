import React from "react"

import { EntitySelection } from "../hooks/helpers/use-entity"
import { SettingsGetter } from "../hooks/helpers/use-get-settings"

import { Main, Title } from "../components/system"
import { SettingsHeader, SettingsBody } from "../components/settings"
import DeliverySitesSettings from "../components/settings/delivery-site-settings"
import ProductionSitesSettings from "../components/settings/production-site-settings"
import DBSCertificateSettings from "../components/settings/2bs-certificates-settings"
import ISCCCertificateSettings from "../components/settings/iscc-certificates-settings"
import CompanySettings from "../components/settings/company-settings"
import useSettings from "../hooks/use-settings"

type SettingsProps = {
  entity: EntitySelection
  settings: SettingsGetter
}

const Settings = ({ entity, settings }: SettingsProps) => {
  const {
    company,
    productionSites,
    deliverySites,
    dbsCertificates,
    isccCertificates,
  } = useSettings(entity, settings)

  const isProducer = entity?.entity_type === "Producteur"
  const isTrader = entity?.entity_type === "Trader"
  const isOperator = entity?.entity_type === "Opérateur"

  const hasCertificates = isProducer || isTrader

  return (
    <Main>
      <SettingsHeader>
        <Title>Paramètres {entity?.name}</Title>
      </SettingsHeader>

      <SettingsBody>
        <CompanySettings entity={entity} settings={company} />

        {hasCertificates && (
          <ISCCCertificateSettings settings={isccCertificates} />
        )}

        {hasCertificates && (
          <DBSCertificateSettings settings={dbsCertificates} />
        )}

        {isProducer && <ProductionSitesSettings settings={productionSites} />}
        {isOperator && <DeliverySitesSettings settings={deliverySites} />}
      </SettingsBody>
    </Main>
  )
}
export default Settings
