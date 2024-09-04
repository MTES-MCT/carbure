import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import { ChargePointStatus } from "./types"

export const useStatus = () => {
  const matchStatus = useMatch("/org/:entity/charge-points/:year/list/:status")

  const status =
    (matchStatus?.params?.status?.toUpperCase() as ChargePointStatus) ||
    ChargePointStatus.Pending

  return status
}

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
