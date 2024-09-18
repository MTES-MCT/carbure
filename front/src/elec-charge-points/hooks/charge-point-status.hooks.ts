import { ChargePointStatus } from "elec-charge-points/types"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"

export const useStatusLabels = () => {
  const { t } = useTranslation()
  const statuses = useMemo(
    () => ({
      [ChargePointStatus.Pending]: t("En attente"),
      [ChargePointStatus.AuditInProgress]: t("En cours d'audit"),
      [ChargePointStatus.Accepted]: t("Accepté"),
    }),
    [t]
  )

  return statuses
}
