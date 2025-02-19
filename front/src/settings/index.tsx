import { useTranslation } from "react-i18next"

import DeliverySitesSettings from "./components/delivery-site/delivery-site"
import ProductionSitesSettings from "./components/production-site"

import useEntity from "carbure/hooks/entity"
import { UserRole } from "carbure/types"
import { Main } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import useTitle from "common/hooks/title"
import { compact } from "common/utils/collection"
import Certificates from "./components/certificates"
import CompanyInfo from "./components/company-info"
import CompanyOptions from "./components/company-options"
import DoubleCountingSettings from "../double-counting/components/settings"
import { EntityUserRights } from "./components/user-rights"
import { ApplicationDetailsDialog } from "double-counting/components/application-details-dialog"
import HashRoute from "common/components/hash-route"
import { AgreementDetailsDialog } from "double-counting/components/agreement-details-dialog"
import useScrollToHash from "common/hooks/scroll-to-hash"
import { usePrivateNavigation } from "common/layouts/navigation"

const Settings = () => {
  const { t } = useTranslation()
  useScrollToHash()
  const entity = useEntity()
  useTitle(`${entity.name} · ${t("Société")}`)
  usePrivateNavigation(t("Paramètres de la société"))
  const { isProducer, isPowerOrHeatProducer, isIndustry } = entity

  const hasCertificates = isIndustry
  const hasDepot = isIndustry || isPowerOrHeatProducer
  const hasOptions = isIndustry

  return (
    <Main>
      <Tabs
        variant="sticky"
        tabs={compact([
          hasOptions && {
            path: "#options",
            key: "options",
            label: t("Options"),
          },
          {
            path: "#info",
            key: "info",
            label: t("Informations"),
          },

          hasCertificates && {
            path: "#certificates",
            key: "certificates",
            label: t("Certificats"),
          },
          isProducer && {
            path: "#production",
            key: "production",
            label: t("Sites de production"),
          },
          hasDepot && {
            path: "#depot",
            key: "depot",
            label: t("Dépôts"),
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
        <CompanyInfo key={entity.id} />
        {hasCertificates && <Certificates />}
        {hasDepot && <DeliverySitesSettings entity={entity} />}
        {isProducer && <ProductionSitesSettings entity={entity} />}
        {isProducer && <DoubleCountingSettings entity={entity} />}
        {entity.hasRights(UserRole.Admin) && <EntityUserRights />}
      </section>
      <HashRoute
        path="double-counting/applications/:id"
        element={<ApplicationDetailsDialog />}
      />
      <HashRoute
        path="double-counting/agreements/:id"
        element={<AgreementDetailsDialog />}
      />
    </Main>
  )
}

export default Settings
