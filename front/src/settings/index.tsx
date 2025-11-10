import { useTranslation } from "react-i18next"

import DeliverySitesSettings from "./pages/delivery-site"
import ProductionSitesSettings from "./pages/production-site"

import useEntity from "common/hooks/entity"
import { UserRole } from "common/types"
import { Content, Main } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import useTitle from "common/hooks/title"
import { compact } from "common/utils/collection"
import Certificates from "./pages/certificates"
import CompanyInfo from "./pages/company-info"
import CompanyOptions from "./pages/company-options"
import { EntityUserRights } from "./pages/user-rights"
import { usePrivateNavigation } from "common/layouts/navigation"
import { useRoutes } from "common/hooks/routes"
import { Navigate, Route, Routes } from "react-router"
import { lazy } from "react"
import { AnnualDeclarationLayout } from "biomethane/layouts/annual-declaration-layout"

const BiomethaneContractPage = lazy(() => import("biomethane/pages/contract"))
const BiomethaneInjectionPage = lazy(() => import("biomethane/pages/injection"))
const BiomethaneProductionPage = lazy(
  () => import("biomethane/pages/production")
)

const Settings = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const entity = useEntity()
  useTitle(`${entity.name} · ${t("Société")}`)
  usePrivateNavigation(t("Paramètres de la société"))

  const {
    isProducer,
    isPowerOrHeatProducer,
    isIndustry,
    isBiomethaneProducer,
  } = entity

  const hasCertificates = isIndustry
  const hasDepot = isIndustry || isPowerOrHeatProducer
  const hasOptions = isIndustry || isBiomethaneProducer
  const defaultTab = hasOptions ? "options" : "info"
  return (
    <Main>
      <Tabs
        tabs={compact([
          hasOptions && {
            path: routes.SETTINGS.OPTIONS,
            key: "options",
            label: t("Options"),
            icon: "ri-settings-2-line",
            iconActive: "ri-settings-2-fill",
          },
          {
            path: routes.SETTINGS.INFO,
            key: "info",
            label: t("Informations"),
            icon: "ri-profile-line",
            iconActive: "ri-profile-fill",
          },
          entity.hasRights(UserRole.Admin) && {
            path: "users",
            key: "users",
            label: t("Utilisateurs"),
            icon: "ri-user-line",
            iconActive: "ri-user-fill",
          },
          isBiomethaneProducer && {
            path: routes.SETTINGS.BIOMETHANE.CONTRACT,
            key: "contract",
            label: t("Contrat"),
            icon: "ri-file-text-line",
            iconActive: "ri-file-text-fill",
          },
          isBiomethaneProducer && {
            path: routes.SETTINGS.BIOMETHANE.PRODUCTION,
            key: "production",
            label: t("Production"),
            icon: "ri-building-line",
            iconActive: "ri-building-fill",
          },
          isBiomethaneProducer && {
            path: routes.SETTINGS.BIOMETHANE.INJECTION,
            key: "injection",
            label: t("Injection"),
            icon: "ri-todo-line",
            iconActive: "ri-todo-fill",
          },
          hasCertificates && {
            path: "certificates",
            key: "certificates",
            label: t("Certificats"),
            icon: "ri-file-text-line",
            iconActive: "ri-file-text-fill",
          },
          isProducer && {
            path: "production",
            key: "production",
            label: t("Sites de production"),
            icon: "ri-building-line",
            iconActive: "ri-building-fill",
          },
          hasDepot && {
            path: "depot",
            key: "depot",
            label: t("Dépôts"),
            icon: "ri-building-4-line",
            iconActive: "ri-building-4-fill",
          },
        ])}
      />
      <Content>
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
          {isBiomethaneProducer && (
            <Route path="biomethane" element={<AnnualDeclarationLayout />}>
              <Route path="contract" element={<BiomethaneContractPage />} />
              <Route path="production" element={<BiomethaneProductionPage />} />
              <Route path="injection" element={<BiomethaneInjectionPage />} />
              <Route index element={<Navigate replace to="contract" />} />
            </Route>
          )}
          <Route path="*" element={<Navigate replace to={defaultTab} />} />
        </Routes>
      </Content>
    </Main>
  )
}

export default Settings
