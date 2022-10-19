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
    <Tag variant={variant} small={small}>
      {label}
    </Tag>
  )
}

export default TicketTag
