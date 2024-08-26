import { CBQueryStates } from "common/hooks/query-builder"
import useTitle from "common/hooks/title"
import { ElecAuditorApplicationsStatus } from "elec-auditor/types"
import { useTranslation } from "react-i18next"



export function usePageTitle(state: CBQueryStates) {
  const { t } = useTranslation()

  const title = t("PDC à auditer")
  const statuses: any = {
    [ElecAuditorApplicationsStatus.AuditInProgress]:
      title + " " + t("en attente"),
    [ElecAuditorApplicationsStatus.AuditDone]:
      title + " " + t("terminé"),
  }
  const entity = state.entity.name
  const year = state.year
  const status = statuses[state.status.toUpperCase()]

  useTitle(`${entity} ∙ ${status} ∙ ${year}`)
}
