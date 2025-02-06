import { SafTicketStatus } from "saf/types"
import { useTranslation } from "react-i18next"
import { usePrivateNavigation } from "common/layouts/navigation"

export const useLayoutTitle = (status: SafTicketStatus) => {
  const { t } = useTranslation()

  const getStatus = () => {
    switch (status) {
      case SafTicketStatus.ACCEPTED:
        return t("Tickets acceptés")
      case SafTicketStatus.PENDING:
        return t("Tickets en attente")
      default:
        return ""
    }
  }

  usePrivateNavigation(getStatus())
}
