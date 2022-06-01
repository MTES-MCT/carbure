import { useTranslation } from "react-i18next"
import { EntityManager } from "carbure/hooks/entity"

import { PortalProvider } from "common-v2/components/portal"
import useDeliverySites from "./hooks/use-delivery-sites"
import useProductionSites from "./hooks/use-production-sites"

import DeliverySitesSettings from "./components/delivery-site"
import ProductionSitesSettings from "./components/production-site"

import CompanyOptions from "./components/company-options"
import CompanyInfo from "./components/company-info"
import Certificates from "./components/certificates"
import EntityUserRights from "./components/user-rights"
import { UserRole } from "carbure/types"
import DoubleCountingSettings from "./components/double-counting"
import useEntity from "carbure/hooks/entity"
import useTitle from "common-v2/hooks/title"
import { Main } from "common-v2/components/scaffold"
import Tabs from "common-v2/components/tabs"
import { compact } from "common-v2/utils/collection"

const Settings = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  useTitle(`${entity.name} · ${t("Société")}`)

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

        <Tabs
          variant="sticky"
          tabs={compact([
            hasOptions && {
              path: "#options",
              key: "options",
              label: t("Options"),
            },
            hasOptions && {
              path: "#info",
              key: "info",
              label: t("Informations"),
            },
            hasCertificates && {
              path: "#certificates",
              key: "certificates",
              label: t("Certificats"),
            },
            hasDepot && {
              path: "#depot",
              key: "depot",
              label: t("Dépôts"),
            },
            isProducer && {
              path: "#production",
              key: "production",
              label: t("Sites de production"),
            },
            isProducer && {
              path: "#double-counting",
              key: "double-counting",
              label: t("Double comptage"),
            },
            entity.hasRights(UserRole.Admin) && {
              path: "#users",
              key: "users",
              label: t("Utilisateurs"),
            },
          ])}
        />
        <section>
          {hasOptions && <CompanyOptions />}
          {hasOptions && <CompanyInfo />}
          {hasCertificates && <Certificates />}
          {hasDepot && <DeliverySitesSettings settings={deliverySites} />}
          {isProducer && <ProductionSitesSettings settings={productionSites} />}
          {isProducer && <DoubleCountingSettings />}
          {entity.hasRights(UserRole.Admin) && <EntityUserRights />}
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
