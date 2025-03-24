import useEntity from "common/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import {
  ArrowGoBackLine,
  ArrowGoForwardLine,
  FileListFill,
  FileListLine,
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
        path: routes.ELEC().CERTIFICATES.PENDING,
        title: t("En attente"),
        additionalInfo: params?.pending_transfer_certificates,
        icon: FileTextLine,
        iconActive: FileTextFill,
        condition: has_elec && isOperator,
      },
      {
        path: routes.ELEC().CERTIFICATES.ACCEPTED,
        title: t("Acceptés"),
        icon: FileListLine,
        iconActive: FileListFill,
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
    condition:
      isAdmin || hasAdminRight("ELEC") || hasAdminRight("TRANSFERRED_ELEC"),
    children: [
      {
        path: routes.ELEC_ADMIN().PROVISION,
        title: t("Certificats"),
        icon: NewsPaperLine,
        iconActive: NewsPaperFill,
        condition: isAdmin || hasAdminRight("ELEC"),
      },
      {
        path: routes.ELEC_ADMIN().TRANSFER,
        title: t("Énergie cédée"),
        icon: ArrowGoForwardLine,
        condition: isAdmin || hasAdminRight("TRANSFERRED_ELEC"),
      },
    ],
  }
  return [elec, elecAdmin]
}
