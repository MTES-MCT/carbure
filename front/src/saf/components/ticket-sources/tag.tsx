import { Tag, TagProps, TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"
import { SafTicketSource } from "saf/types"

export interface TicketSourceTagProps extends TagProps {
  ticketSource: SafTicketSource
}

export const TicketSourceTag = ({
  ticketSource,
  ...props
}: TicketSourceTagProps) => {
  const { t } = useTranslation()

  const available_volume =
    ticketSource.total_volume - ticketSource.assigned_volume
  let label
  let variant: TagVariant

  if (available_volume > 0) {
    label = t("Disponible")
    variant = "success"
  } else {
    label = t("Affecté")
    variant = "info"
  }

  return (
    <Tag {...props} variant={variant}>
      {label}
    </Tag>
  )
}

export default TicketSourceTag
