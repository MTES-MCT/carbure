import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"
import { useTranslation } from "react-i18next"
import { SafTicketSource, SafTicketSourcePreview } from "saf/types"

export interface TicketSourceTagProps {
  ticketSource: SafTicketSourcePreview | SafTicketSource | undefined
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
  let variant: BadgeProps["severity"]

  if (available_volume > 0) {
    label = t("Disponible")
    variant = "success"
  } else {
    label = t("Affecté")
    variant = "info"
  }

  return (
    <Badge {...props} severity={variant} noIcon>
      {label}
    </Badge>
  )
}

export default TicketSourceTag
