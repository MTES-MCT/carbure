import { Tabs } from "common/components/tabs2"
import { useTranslation } from "react-i18next"
import { useDeclarationDetailRoutes } from "../hooks/use-declaration-detail-routes"

export const DeclarationDetailTabs = () => {
  const { t } = useTranslation()
  const declarationDetailRoutes = useDeclarationDetailRoutes()

  return (
    <Tabs
      tabs={[
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
        {
          key: "contract",
          label: t("Contrat"),
          path: declarationDetailRoutes.CONTRACT,
        },
        {
          key: "contacts",
          label: t("Contacts"),
          path: declarationDetailRoutes.CONTACTS,
        },
      ]}
    />
  )
}
