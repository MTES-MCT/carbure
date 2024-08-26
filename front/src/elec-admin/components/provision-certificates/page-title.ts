import { CBQueryStates } from "common/hooks/query-builder"
import useTitle from "common/hooks/title"
import {
  ElecAdminProvisionCertificateStatus
} from "elec-admin/types"
import { useTranslation } from "react-i18next"

export function usePageTitle(state: CBQueryStates) {
  const { t } = useTranslation()

  const statuses: any = {
    [ElecAdminProvisionCertificateStatus.Available]: t("Énergie attribuée"),
    [ElecAdminProvisionCertificateStatus.History]: t("Énergie cédée"),
  }

  const entity = state.entity.name
  const year = state.year
  const status = statuses[state.status.toUpperCase()]

  useTitle(`${entity} ∙ ${status} ${year}`)
}
