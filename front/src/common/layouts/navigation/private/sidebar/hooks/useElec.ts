import useEntity from "common/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"
import { MenuSection } from "../sidebar.types"
import { ArrowGoBackLine, ArrowGoForwardLine } from "common/components/icon"
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

  const elecCerts: MenuSection = {
    title: t("Certificats d'électricité"),
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
        additionalInfo: params?.pending_transfer_certificates,
      },
    ],
  }

  return [elecCerts]
}
