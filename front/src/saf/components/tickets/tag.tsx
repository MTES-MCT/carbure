import { Tag, TagProps, TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"
import { SafTicket, SafTicketSource, SafTicketStatus } from "saf/types"

export interface TicketTagProps extends TagProps {
  status: SafTicketStatus
  small?: boolean
}

export const TicketTag = ({ status, small }: TicketTagProps) => {
  const { t } = useTranslation()

  let label
  let variant: TagVariant

  switch (status) {
    case SafTicketStatus.Accepted:
      label = t("Accepté")
      variant = "success"
      break

    case SafTicketStatus.Pending:
      label = t("En attente")
      variant = "info"
      break

    case SafTicketStatus.Rejected:
      label = t("Refusé")
      variant = "danger"
      break

    default:
      label = t("N/A")
      variant = "danger"
      break
  }

  return (
    <Tag variant={variant} small={small}>
      {label}
    </Tag>
  )
}

export default TicketTag
