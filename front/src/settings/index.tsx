import { EntitySelection } from "carbure/hooks/use-entity"
import { SettingsGetter } from "./hooks/use-get-settings"

import use2BSCertificates from "./hooks/use-2bs-certificates"
import useCompany from "./hooks/use-company"
import useDeliverySites from "./hooks/use-delivery-sites"
import useISCCCertificates from "./hooks/use-iscc-certificates"
import useNationalSystemCertificates from "./hooks/use-national-system-certificates"
import useProductionSites from "./hooks/use-production-sites"

import { Main, Title } from "common/components"
import { SettingsHeader, SettingsBody } from "./components/common"
import DeliverySitesSettings from "./components/delivery-site"
import ProductionSitesSettings from "./components/production-site"
import {
  DBSCertificateSettings,
  ISCCCertificateSettings,
  REDCertCertificateSettings,
  SNCertificateSettings,
} from "./components/certificates"
import CompanySettings from "./components/company"
import Sticky from "common/components/sticky"
import useREDCertCertificates from "./hooks/use-redcert-certificates"

function useSettings(entity: EntitySelection, settings: SettingsGetter) {
  const company = useCompany(entity, settings)
  const productionSites = useProductionSites(entity)
  const deliverySites = useDeliverySites(entity)
  const dbsCertificates = use2BSCertificates(entity, productionSites)
  const isccCertificates = useISCCCertificates(entity, productionSites)
  const redcertCertificates = useREDCertCertificates(entity, productionSites)
  const nationalSystemCertificates = useNationalSystemCertificates(entity, productionSites) // prettier-ignore

  return {
    productionSites,
    deliverySites,
    dbsCertificates,
    isccCertificates,
    redcertCertificates,
    nationalSystemCertificates,
    company,
  }
}

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
    redcertCertificates,
    nationalSystemCertificates,
  } = useSettings(entity, settings)

  const isProducer = entity?.entity_type === "Producteur"
  const isTrader = entity?.entity_type === "Trader"
  const isOperator = entity?.entity_type === "Opérateur"

  const hasCertificates = isProducer || isTrader
  const hasCSN = isProducer || isOperator

  return (
    <Main>
      <SettingsHeader>
        <Title>{entity?.name}</Title>
      </SettingsHeader>

      <Sticky>
        <a href="#options">Options</a>
        <a href="#depot">Dépôts</a>
        {isProducer && <a href="#production">Sites de production</a>}
        {hasCertificates && <a href="#iscc">Certificats ISCC</a>}
        {hasCertificates && <a href="#2bs">Certificats 2BS</a>}
        {hasCertificates && <a href="#red">Certificats REDcert</a>}
        {hasCertificates && <a href="#sn">Certificats Système National</a>}
        {!hasCertificates && hasCSN && <a href="#sn">Certificats Système National</a>}
      </Sticky>

      <SettingsBody>
        <CompanySettings entity={entity} settings={company} />
        <DeliverySitesSettings settings={deliverySites} />

        {isProducer && <ProductionSitesSettings settings={productionSites} />}

        {hasCertificates && (
          <ISCCCertificateSettings settings={isccCertificates} />
        )}

        {hasCertificates && (
          <DBSCertificateSettings settings={dbsCertificates} />
        )}

        {hasCertificates && (
          <REDCertCertificateSettings settings={redcertCertificates} />
        )}

        {(hasCertificates || hasCSN) && (
          <SNCertificateSettings settings={nationalSystemCertificates} />
        )}
      </SettingsBody>
    </Main>
  )
}
export default Settings
