import { useTranslation } from "react-i18next"

import DeliverySitesSettings from "./components/delivery-site"
import ProductionSitesSettings from "./components/production-site"

import useEntity from "carbure/hooks/entity"
import { UserRole } from "carbure/types"
import { getEntityTypeLabel } from "carbure/utils/normalizers"
import { Main } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import useTitle from "common/hooks/title"
import { compact } from "common/utils/collection"
import Certificates from "./components/certificates"
import CompanyInfo from "./components/company-info"
import CompanyOptions from "./components/company-options"
import DoubleCountingSettings from "../double-counting/components/settings"
import EntityUserRights from "./components/user-rights"
import ElecChargePointsSettings from "../elec/components/charge-points/settings"
import { ApplicationDetailsDialog } from "double-counting/components/application-details-dialog"
import HashRoute from "common/components/hash-route"
import { AgreementDetailsDialog } from "double-counting/components/agreement-details-dialog"
import ElecMeterReadingsSettings from "elec/components/meter-readings/settings"

const Settings = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  useTitle(`${entity.name} · ${t("Société")}`)

  const { isProducer, isPowerOrHeatProducer, isCPO, isIndustry } = entity

  const hasCertificates = isIndustry
  const hasDepot = isIndustry || isPowerOrHeatProducer
  const hasOptions = isIndustry

  return (
    <Main>
      <header>
        <h1>
          {entity.name} · {getEntityTypeLabel(entity.entity_type)}
        </h1>
      </header>

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
          isCPO && {
            path: "#elec-charge-points",
            key: "elec-charge-points",
            label: t("Points de recharge"),
          },
          isCPO && {
            path: "#elec-meter-readings",
            key: "elec-meter-readings",
            label: t("Relevés trimestriels"),
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
        {isProducer && <DoubleCountingSettings />}
        {isCPO && <ElecChargePointsSettings companyId={entity.id} />}
        {isCPO && <ElecMeterReadingsSettings companyId={entity.id} />}
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
