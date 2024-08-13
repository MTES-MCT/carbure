import useTitle from "common/hooks/title"
import {
  ElecAdminTransferCertificateStates
} from "elec-admin/types"
import { ElecTransferCertificateStatus } from "elec/types-cpo"
import { title } from "process"
import { useTranslation } from "react-i18next"


export function usePageTitle(state: ElecAdminTransferCertificateStates) {
  const { t } = useTranslation()

  const title = t("Énergie cédée")
  const statuses: any = {
    [ElecTransferCertificateStatus.Pending]:
      title + " " + t("en attente"),
    [ElecTransferCertificateStatus.Accepted]:
      title + " " + t("acceptée"),
    [ElecTransferCertificateStatus.Rejected]:
      title + " " + t("rejetée"),
  }
  const entity = state.entity.name
  const year = state.year
  const status = statuses[state.status.toUpperCase()]

  useTitle(`${entity} ∙ ${status} ∙ ${year}`)
}
