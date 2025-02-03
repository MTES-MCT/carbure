import { EtsStatusEnum } from "api-schema"
import { Certificate } from "common/components/icons"
import { Tag, TagProps, TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"
import { SafTicketStatus } from "saf/types"

export interface TicketTagProps extends TagProps {
  status?: SafTicketStatus
  ets?: EtsStatusEnum | null
}

export const TicketTag = ({ status, ets, small, big }: TicketTagProps) => {
  const { t } = useTranslation()

  let label
  let variant: TagVariant
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
      variant = "danger"
      break

    default:
      label = t("N/A")
      variant = "none"
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
    <Tag variant={variant} small={small} big={big}>
      {declared && <Certificate />}
      {label}
    </Tag>
  )
}

export default TicketTag
