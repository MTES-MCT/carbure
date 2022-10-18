import { Tag, TagProps, TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"
import { SafTicketSource } from "saf/types"

export interface TicketSourceTagProps extends TagProps {
  ticketSource: SafTicketSource | undefined
}

export const TicketSourceTag = ({
  ticketSource,
  ...props
}: TicketSourceTagProps) => {
  const { t } = useTranslation()

  if (!ticketSource) return null

  const available_volume =
    ticketSource.total_volume - ticketSource.assigned_volume
  let label
  let variant: TagVariant

  if (available_volume > 0) {
    label = t("Disponible")
    variant = "success"
  } else {
    label = t("Affecté")
    variant = "none"
  }

  return (
    <Tag {...props} variant={variant}>
      {label}
    </Tag>
  )
}

export default TicketSourceTag
