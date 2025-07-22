import { useTranslation } from "react-i18next"

import DeliverySitesSettings from "./components/delivery-site/delivery-site"
import ProductionSitesSettings from "./components/production-site"

import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"
import { Content, Main } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import useTitle from "common/hooks/title"
import { compact } from "common/utils/collection"
import Certificates from "./components/certificates"
import CompanyInfo from "./components/company-info"
import CompanyOptions from "./components/company-options"
import { EntityUserRights } from "./components/user-rights"
import { ApplicationDetailsDialog } from "double-counting/components/application-details-dialog"
import HashRoute from "common/components/hash-route"
import { AgreementDetailsDialog } from "double-counting/components/agreement-details-dialog"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useRoutes } from "common/hooks/routes"
import { Navigate, Route, Routes } from "react-router-dom"

const Settings = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const entity = useEntity()
  useTitle(`${entity.name} · ${t("Société")}`)
  usePrivateNavigation(t("Paramètres de la société"))

  const { isProducer, isPowerOrHeatProducer, isIndustry } = entity

  const hasCertificates = isIndustry
  const hasDepot = isIndustry || isPowerOrHeatProducer
  const hasOptions = isIndustry
  const defaultTab = hasOptions ? "options" : "info"
  return (
    <Main>
      <Tabs
        tabs={compact([
          hasOptions && {
            path: routes.SETTINGS.OPTIONS,
            key: "options",
            label: t("Options"),
          },
          {
            path: routes.SETTINGS.INFO,
            key: "info",
            label: t("Informations"),
          },

          hasCertificates && {
            path: "certificates",
            key: "certificates",
            label: t("Certificats"),
          },
          isProducer && {
            path: "production",
            key: "production",
            label: t("Sites de production"),
          },
          hasDepot && {
            path: "depot",
            key: "depot",
            label: t("Dépôts"),
          },
          entity.hasRights(UserRole.Admin) && {
            path: "users",
            key: "users",
            label: t("Utilisateurs"),
          },
        ])}
      />
      <Content>
        <HashRoute
          path="double-counting/applications/:id"
          element={<ApplicationDetailsDialog />}
        />
        <HashRoute
          path="double-counting/agreements/:id"
          element={<AgreementDetailsDialog />}
        />

        <Routes>
          {hasOptions && <Route path="options" element={<CompanyOptions />} />}
          <Route path="info" element={<CompanyInfo />} />
          {hasCertificates && (
            <Route path="certificates" element={<Certificates />} />
          )}
          {hasDepot && (
            <Route
              path="depot"
              element={<DeliverySitesSettings entity={entity} />}
            />
          )}
          {isProducer && (
            <Route
              path="production"
              element={<ProductionSitesSettings entity={entity} />}
            />
          )}
          {entity.hasRights(UserRole.Admin) && (
            <Route path="users" element={<EntityUserRights />} />
          )}

          <Route path="*" element={<Navigate replace to={defaultTab} />} />
        </Routes>
      </Content>
    </Main>
  )
}

export default Settings
