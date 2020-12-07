import React from "react"

import { EntitySelection } from "common/hooks/helpers/use-entity"
import { SettingsGetter } from "./hooks/use-get-settings"

import { Main, Title } from "common/system"
import { SettingsHeader, SettingsBody } from "./components/common"
import DeliverySitesSettings from "./components/delivery-site-settings"
import ProductionSitesSettings from "./components/production-site-settings"
import DBSCertificateSettings from "./components/2bs-certificates-settings"
import ISCCCertificateSettings from "./components/iscc-certificates-settings"
import NationalSystemCertificatesSettings from "./components/national-system-certificates-settings"
import CompanySettings from "./components/company-settings"
import useSettings from "./hook"

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
    nationalSystemCertificates,
  } = useSettings(entity, settings)

  const isProducer = entity?.entity_type === "Producteur"
  const isTrader = entity?.entity_type === "Trader"
  const isOperator = entity?.entity_type === "Opérateur"

  const hasCertificates = isProducer || isTrader

  return (
    <Main>
      <SettingsHeader>
        <Title>{entity?.name}</Title>
      </SettingsHeader>

      <SettingsBody>
        {(isProducer || isTrader || isOperator) && (
          <CompanySettings entity={entity} settings={company} />
        )}

        {(isProducer || isTrader || isOperator) && (
          <DeliverySitesSettings settings={deliverySites} />
        )}

        {isProducer && <ProductionSitesSettings settings={productionSites} />}

        {hasCertificates && (
          <ISCCCertificateSettings settings={isccCertificates} />
        )}

        {hasCertificates && (
          <DBSCertificateSettings settings={dbsCertificates} />
        )}

        {((isProducer && entity?.has_mac) || isOperator) && (
          <NationalSystemCertificatesSettings
            settings={nationalSystemCertificates}
          />
        )}
      </SettingsBody>
    </Main>
  )
}
export default Settings
