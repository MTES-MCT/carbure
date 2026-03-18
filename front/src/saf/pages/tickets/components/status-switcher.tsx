import { Tab, Tabs } from "common/components/tabs2"
import useEntity from "common/hooks/entity"
import { useTranslation } from "react-i18next"
import { SafSnapshot, SafTicketType, SafTicketStatus } from "saf/types"

interface StatusSwitcherProps {
  status?: SafTicketStatus
  count?: SafSnapshot
  type: SafTicketType
  onSwitch: (status: SafTicketStatus) => void
}

export const StatusSwitcher = ({
  status,
  count,
  type,
}: StatusSwitcherProps) => {
  const { t } = useTranslation()

  const entity = useEntity()
  const tabs: Tab<string>[] = []

  const isAdmin =
    entity.isAdmin || (entity.isExternal && entity.hasAdminRight("AIRLINE"))

  if (type === "received") {
    tabs.push(
      {
        key: SafTicketStatus.PENDING,
        path: `../tickets-received/pending`,
        label: `${t("En attente")} (${count?.tickets_received_pending ?? 0})`,
        icon: "fr-icon-draft-line",
        iconActive: "fr-icon-draft-fill",
      },
      {
        key: SafTicketStatus.ACCEPTED,
        path: `../tickets-received/accepted`,
        label: `${t("Accepté")} (${count?.tickets_received_accepted ?? 0})`,
        icon: "fr-icon-check-line",
        iconActive: "fr-icon-check-line",
      }
    )
  } else if (type === "assigned") {
    if (isAdmin) {
      tabs.push({
        key: "all",
        path: `../tickets-assigned/all`,
        label: `${t("Tous")} (${count?.tickets_assigned})`,
        icon: "fr-icon-layout-grid-line",
        iconActive: "fr-icon-layout-grid-fill",
      })
    }

    tabs.push(
      {
        key: SafTicketStatus.PENDING,
        path: `../tickets-assigned/pending`,
        label: `${t("En attente")} (${count?.tickets_assigned_pending ?? 0})`,
        icon: "fr-icon-draft-line",
        iconActive: "fr-icon-draft-fill",
      },
      {
        key: SafTicketStatus.REJECTED,
        path: `../tickets-assigned/rejected`,
        label: `${t("Refusé")} (${count?.tickets_assigned_rejected ?? 0})`,
        icon: "fr-icon-chat-delete-line",
        iconActive: "fr-icon-chat-delete-line",
      },
      {
        key: SafTicketStatus.ACCEPTED,
        path: `../tickets-assigned/accepted`,
        label: `${t("Accepté")} (${count?.tickets_assigned_accepted ?? 0})`,
        icon: "fr-icon-check-line",
        iconActive: "fr-icon-check-line",
      }
    )
  }

  return <Tabs keepSearch focus={status} tabs={tabs} />
}
