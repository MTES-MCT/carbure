import { usePrivateNavigation } from "common/layouts/navigation"
import { AdminStatus } from "controls/types"
import { useTranslation } from "react-i18next"
import { Status } from "transactions/types"

export const useLotsTitleNavigation = (status: Status) => {
  const { t } = useTranslation()
  const statuses: Record<Status, string> = {
    drafts: t("Brouillons"),
    in: t("Reçus"),
    out: t("Envoyés"),
    stocks: t("En stock"),
    declaration: "",
    unknown: "",
  }

  // TODO: Add translations when admin sidebar will be ready
  const adminStatuses: Record<AdminStatus, string> = {
    alerts: t("Signalements"),
    lots: t("Lots"),
    stocks: t("En stock"),
    unknown: "",
  }

  const computedStatus =
    status in statuses
      ? statuses[status]
      : (adminStatuses[status as AdminStatus] ?? "")

  usePrivateNavigation(computedStatus)
}
