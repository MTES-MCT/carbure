import { CBQueryStates } from "common/hooks/query-builder"
import useTitle from "common/hooks/title"
import { ElecAdminAuditStatus } from "elec-audit-admin/types"
import { useTranslation } from "react-i18next"

export function usePageTitle(state: CBQueryStates) {
  const { t } = useTranslation()

  const title = "Relevés des points de recharge"
  const statuses: any = {
    [ElecAdminAuditStatus.Pending]: t(title) + " " + t("en attente"),
    [ElecAdminAuditStatus.AuditInProgress]:
      t(title) + " " + t("Audit en cours"),
    [ElecAdminAuditStatus.AuditDone]: t(title) + " " + t("Audit terminé"),
    [ElecAdminAuditStatus.History]: t(title) + " " + t("historique"),
  }
  const entity = state.entity.name
  const year = state.year
  const status = statuses[state.status.toUpperCase()]

  useTitle(`${entity} ∙ ${status} ${year}`)
}
