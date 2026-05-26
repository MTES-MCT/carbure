import { Tabs } from "common/components/tabs2"
import { useTranslation } from "react-i18next"
import { useDeclarationDetailRoutes } from "../hooks/use-declaration-detail-routes"
import { useBiomethanePermissions } from "biomethane/hooks/use-biomethane-permissions"
import { compact } from "common/utils/collection"

export const DeclarationDetailTabs = () => {
  const { t } = useTranslation()
  const declarationDetailRoutes = useDeclarationDetailRoutes()
  const { adminPermissions } = useBiomethanePermissions()

  return (
    <Tabs
      tabs={compact([
        {
          key: "digestate",
          label: t("Digestat"),
          path: declarationDetailRoutes.DIGESTATE,
        },
        {
          key: "energy",
          label: t("Énergie"),
          path: declarationDetailRoutes.ENERGY,
        },
        {
          key: "supply-plan",
          label: t("Approvisionnement"),
          path: declarationDetailRoutes.SUPPLY_PLAN,
        },
        adminPermissions.canAccessContract && {
          key: "contract",
          label: t("Contrat"),
          path: declarationDetailRoutes.CONTRACT,
        },
        {
          key: "production",
          label: t("Production"),
          path: declarationDetailRoutes.PRODUCTION,
        },
        adminPermissions.canAccessInjection && {
          key: "injection",
          label: t("Site d'injection"),
          path: declarationDetailRoutes.INJECTION,
        },
        {
          key: "users",
          label: t("Utilisateurs"),
          path: declarationDetailRoutes.USERS,
        },
        {
          key: "contacts",
          label: t("Contacts"),
          path: declarationDetailRoutes.CONTACTS,
        },
      ])}
    />
  )
}
