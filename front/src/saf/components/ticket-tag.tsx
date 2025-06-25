import { EtsStatusEnum } from "api-schema"
import { Certificate } from "common/components/icons"
import { useTranslation } from "react-i18next"
import { SafTicketStatus } from "saf/types"
import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"
export interface TicketTagProps {
  status?: SafTicketStatus
  ets?: EtsStatusEnum | null
  small?: boolean
}

export const TicketTag = ({ status, ets, small = false }: TicketTagProps) => {
  const { t } = useTranslation()

  let label
  let variant: BadgeProps["severity"]
  let declared = false

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
      variant = "error"
      break

    default:
      label = t("N/A")
      variant = "info"
      break
  }

  switch (ets) {
    case EtsStatusEnum.ETS_VALUATION:
      declared = true
      label = t("ETS")
      break

    // case EtsStatusEnum.OUTSIDE_ETS:
    //   declared = true
    //   label = t("Schéma volontaire")
    //   break
  }

  return (
    <Badge severity={variant} noIcon small={small}>
      {declared && <Certificate />}
      {label}
    </Badge>
  )
}

export default TicketTag
