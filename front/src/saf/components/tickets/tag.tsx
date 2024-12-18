import { Tag, TagProps, TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"
import { SafTicketStatus } from "saf/types"

export interface TicketTagProps extends TagProps {
  status?: SafTicketStatus
}

export const TicketTag = ({ status, small, big }: TicketTagProps) => {
  const { t } = useTranslation()

  let label
  let variant: TagVariant

  switch (status) {
    case SafTicketStatus.ACCEPTED:
      label = t("Accepté")
      variant = "success"
      break

    case SafTicketStatus.PENDING:
      label = t("En attente")
      variant = "info"
      break

    case SafTicketStatus.REJECTED:
      label = t("Refusé")
      variant = "danger"
      break

    default:
      label = t("N/A")
      variant = "none"
      break
  }

  return (
    <Tag variant={variant} small={small} big={big}>
      {label}
    </Tag>
  )
}

export default TicketTag
