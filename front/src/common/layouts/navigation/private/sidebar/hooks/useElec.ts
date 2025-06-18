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
  const entity = useEntity()
  const { t } = useTranslation()
  const routes = useRoutes()

  const { isAdmin, isCPO } = entity
  const isElecOperator = entity.isOperator && entity.has_elec
  const isElecAdmin = entity.isExternal && entity.hasAdminRight("ELEC")
  const isElecTransferAdmin = entity.isExternal && entity.hasAdminRight("TRANSFERRED_ELEC") // prettier-ignore

  const elec: MenuSection = {
    title: t("Certificats d'électricité"),
    condition: isElecOperator || isCPO,
    children: [
      {
        path: routes.ELEC().CERTIFICATES.PENDING,
        title: t("En attente"),
        additionalInfo: params?.pending_transfer_certificates,
        icon: FileTextLine,
        iconActive: FileTextFill,
        condition: isElecOperator,
      },
      {
        path: routes.ELEC().CERTIFICATES.ACCEPTED,
        title: t("Acceptés"),
        icon: FileListLine,
        iconActive: FileListFill,
        condition: isElecOperator,
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
    condition: isAdmin || isElecAdmin || isElecTransferAdmin,
    children: [
      {
        path: routes.ELEC_ADMIN().PROVISION,
        title: t("Certificats"),
        icon: NewsPaperLine,
        iconActive: NewsPaperFill,
        condition: isAdmin || isElecAdmin,
      },
      {
        path: routes.ELEC_ADMIN().TRANSFER,
        title: t("Énergie cédée"),
        icon: ArrowGoForwardLine,
        condition: isAdmin || isElecTransferAdmin,
      },
    ],
  }

  const elecV2: MenuSection = {
    title: t("Certificats d'élec (v2)"),
    condition:
      isCPO || isElecOperator || isAdmin || isElecAdmin || isElecTransferAdmin,
    children: [
      {
        path: routes.ELEC_V2().CERTIFICATES.PROVISION,
        title: t("Cert. de fourniture"),
        icon: ArrowGoForwardLine,
        condition: isCPO || isAdmin || isElecAdmin,
      },
      {
        path: routes.ELEC_V2().CERTIFICATES.TRANSFER,
        title: t("Cert. de cession"),
        icon: ArrowGoBackLine,
      },
    ],
  }

  return [elec, elecAdmin, elecV2]
}
