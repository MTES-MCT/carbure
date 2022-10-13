import { Tag, TagProps, TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"
import { SafTicket, SafTicketSource, SafTicketStatus } from "saf/types"

export interface TicketTagProps extends TagProps {
  ticket: SafTicket
  status: SafTicketStatus
}

export const TicketTag = ({ ticket, status, ...props }: TicketTagProps) => {
  const { t } = useTranslation()

  let label = t("N/A")
  let variant: TagVariant | undefined = undefined

  if (status === SafTicketStatus.Accepted) {
    label = t("Accepté")
    variant = "success"
  } else if (status === SafTicketStatus.Pending) {
    label = t("En attente")
    variant = "info"
  } else {
    label = t("Refusé")
    variant = "danger"
  }

  return (
    <Tag {...props} variant={variant}>
      {label}
    </Tag>
  )
}

export default TicketTag
