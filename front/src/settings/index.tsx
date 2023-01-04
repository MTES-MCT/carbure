import { useTranslation } from "react-i18next"

import DeliverySitesSettings from "./components/delivery-site"
import ProductionSitesSettings from "./components/production-site"

import CompanyOptions from "./components/company-options"
import CompanyInfo from "./components/company-info"
import Certificates from "./components/certificates"
import EntityUserRights from "./components/user-rights"
import { UserRole } from "carbure/types"
import DoubleCountingSettings from "./components/double-counting"
import useEntity from "carbure/hooks/entity"
import useTitle from "common/hooks/title"
import { Main } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { getEntityTypeLabel } from "carbure/utils/normalizers"

const Settings = () => {
  const { t } = useTranslation()

  const entity = useEntity()
  useTitle(`${entity.name} · ${t("Société")}`)

  const { isProducer, isTrader, isOperator } = entity

  const hasCertificates = isProducer || isTrader || isOperator
  const hasDepot = isProducer || isOperator || isTrader
  const hasOptions = isProducer || isOperator || isTrader

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
        {hasOptions && <CompanyInfo />}
        {hasCertificates && <Certificates />}
        {hasDepot && <DeliverySitesSettings entity={entity} />}
        {isProducer && <ProductionSitesSettings entity={entity} />}
        {isProducer && <DoubleCountingSettings />}
        {entity.hasRights(UserRole.Admin) && <EntityUserRights />}
      </section>
    </Main>
  )
}

export default Settings
