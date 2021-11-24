import { Trans } from "react-i18next"
import { EntityManager } from "carbure/hooks/entity"
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
import UserRights from "./components/user-rights"
import { UserRole } from "common/types"
import DoubleCountingSettings from "./components/double-counting"
import useEntity from "carbure/hooks/entity"

const Settings = () => {
  const entity = useEntity()

  const {
    company,
    productionSites,
    deliverySites,
    dbsCertificates,
    isccCertificates,
    redcertCertificates,
    nationalSystemCertificates,
  } = useSettings(entity)

  const { isProducer, isTrader, isOperator } = entity

  const hasCertificates = isProducer || isTrader
  const hasCSN = isProducer || isOperator
  const hasDepot = isProducer || isOperator || isTrader
  const hasOptions = isProducer || isOperator || isTrader

  return (
    <Main>
      <SettingsHeader>
        <Title>{entity?.name}</Title>
      </SettingsHeader>

      <Sticky>
        {hasOptions && (
          <a href="#options">
            <Trans>Options</Trans>
          </a>
        )}
        {hasDepot && (
          <a href="#depot">
            <Trans>Dépôts</Trans>
          </a>
        )}
        {isProducer && (
          <a href="#production">
            <Trans>Sites de production</Trans>
          </a>
        )}
        {isProducer && (
          <a href="#double-counting">
            <Trans>Double comptage</Trans>
          </a>
        )}
        {hasCertificates && (
          <a href="#iscc">
            <Trans>ISCC</Trans>
          </a>
        )}
        {hasCertificates && (
          <a href="#2bs">
            <Trans>2BS</Trans>
          </a>
        )}
        {hasCertificates && (
          <a href="#red">
            <Trans>REDcert</Trans>
          </a>
        )}
        {(hasCertificates || (!hasCertificates && hasCSN)) && (
          <a href="#sn">
            <Trans>Système National</Trans>
          </a>
        )}
        {entity.hasRights(UserRole.Admin) && (
          <a href="#users">
            <Trans>Utilisateurs</Trans>
          </a>
        )}
      </Sticky>

      <SettingsBody>
        {hasOptions && <CompanySettings entity={entity} settings={company} />}
        {hasDepot && <DeliverySitesSettings settings={deliverySites} />}

        {isProducer && <ProductionSitesSettings settings={productionSites} />}

        {isProducer && (
          <DoubleCountingSettings entity={entity} settings={company} />
        )}

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

        {entity.hasRights(UserRole.Admin) && <UserRights entity={entity} />}
      </SettingsBody>
    </Main>
  )
}

function useSettings(entity: EntityManager) {
  const company = useCompany(entity)
  const productionSites = useProductionSites(entity)
  const deliverySites = useDeliverySites(entity)
  const dbsCertificates = use2BSCertificates(entity, productionSites, company)
  const isccCertificates = useISCCCertificates(entity, productionSites, company)
  const redcertCertificates = useREDCertCertificates(entity, productionSites, company) // prettier-ignore
  const nationalSystemCertificates = useNationalSystemCertificates(entity, productionSites, company) // prettier-ignore

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

export default Settings
