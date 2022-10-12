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

  let label = t("N/A")
  let variant: TagVariant | undefined = undefined
  const available_volume =
    ticketSource.total_volume - ticketSource.assigned_volume

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
