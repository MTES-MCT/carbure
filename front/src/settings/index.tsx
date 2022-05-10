import { Trans, useTranslation } from "react-i18next"
import { EntityManager } from "carbure/hooks/entity"

import { PortalProvider } from "common-v2/components/portal"
import useDeliverySites from "./hooks/use-delivery-sites"
import useProductionSites from "./hooks/use-production-sites"

import DeliverySitesSettings from "./components/delivery-site"
import ProductionSitesSettings from "./components/production-site"

import CompanyOptions from "./components/company-options"
import CompanyInfo from "./components/company-info"
import Certificates from "./components/certificates"
import Sticky from "common/components/sticky"
import EntityUserRights from "./components/user-rights"
import { UserRole } from "carbure/types"
import DoubleCountingSettings from "./components/double-counting"
import useEntity from "carbure/hooks/entity"
import useTitle from "common-v2/hooks/title"
import { Main } from "common-v2/components/scaffold"

const Settings = () => {
  const { t } = useTranslation()
  useTitle(t("Société"))

  const entity = useEntity()

  const { productionSites, deliverySites } = useSettings(entity)

  const { isProducer, isTrader, isOperator } = entity

  const hasCertificates = isProducer || isTrader || isOperator
  const hasDepot = isProducer || isOperator || isTrader
  const hasOptions = isProducer || isOperator || isTrader

  return (
    <PortalProvider>
      <Main>
        <header>
          <h1>{entity?.name}</h1>
        </header>

        <Sticky>
          {hasOptions && (
            <a href="#options">
              <Trans>Options</Trans>
            </a>
          )}
          {hasOptions && (
            <a href="#info">
              <Trans>Informations</Trans>
            </a>
          )}
          {hasCertificates && (
            <a href="#certificates">
              <Trans>Certificats</Trans>
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
          {entity.hasRights(UserRole.Admin) && (
            <a href="#users">
              <Trans>Utilisateurs</Trans>
            </a>
          )}
        </Sticky>

        <section>
          {hasOptions && <CompanyOptions />}
          {hasOptions && <CompanyInfo />}
          {hasCertificates && <Certificates />}
          {hasDepot && <DeliverySitesSettings settings={deliverySites} />}
          {isProducer && <ProductionSitesSettings settings={productionSites} />}
          {isProducer && <DoubleCountingSettings />}
          {entity.hasRights(UserRole.Admin) && (
            <EntityUserRights entity={entity} />
          )}
        </section>
      </Main>
    </PortalProvider>
  )
}

function useSettings(entity: EntityManager) {
  const productionSites = useProductionSites(entity)
  const deliverySites = useDeliverySites(entity)

  return {
    productionSites,
    deliverySites,
  }
}

export default Settings
