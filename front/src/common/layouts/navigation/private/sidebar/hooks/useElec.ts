import useEntity from "carbure/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import {
  ArrowGoBackLine,
  ArrowGoForwardLine,
  FileTextFill,
  FileTextLine,
  NewsPaperFill,
  NewsPaperLine,
} from "common/components/icon"
import { apiTypes } from "common/services/api-fetch.types"

type ElecParams = Pick<apiTypes["NavStats"], "pending_transfer_certificates">
export const useElec = (params?: ElecParams) => {
  const { has_elec, isOperator, isCPO, isAdmin, hasAdminRight } = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const elec: MenuSection = {
    title: t("Certificats d'électricité"),
    condition: (has_elec && isOperator) || isCPO,
    children: [
      {
        path: routes.ELEC().CERTIFICATES,
        title: t("Certificats"),
        additionalInfo: params?.pending_transfer_certificates,
        icon: FileTextLine,
        iconActive: FileTextFill,
        condition: has_elec && isOperator,
      },
      {
        path: routes.ELEC().PROVISIONNED_ENERGY,
        title: t("Énergie disponible"),
        icon: ArrowGoBackLine,
        condition: isCPO,
      },
      {
        path: routes.ELEC().TRANSFERRED_ENERGY,
        title: t("Énergie cédée"),
        icon: ArrowGoForwardLine,
        condition: isCPO,
      },
    ],
  }

  const elecAdmin: MenuSection = {
    title: t("Électricité"),
    condition: isAdmin || hasAdminRight("ELEC"),
    children: [
      {
        path: routes.ELEC_ADMIN().PROVISION,
        title: t("Certificats"),
        icon: NewsPaperLine,
        iconActive: NewsPaperFill,
      },
      {
        path: routes.ELEC_ADMIN().TRANSFER,
        title: t("Énergie cédée"),
        icon: ArrowGoForwardLine,
      },
    ],
  }
  return [elec, elecAdmin]
}
