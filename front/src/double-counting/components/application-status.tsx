import { BadgeProps, Badge } from "@codegouvfr/react-dsfr/Badge"
import { useTranslation } from "react-i18next"
import {
  DoubleCountingStatus as DCStatus,
  DoubleCountingExtendedStatus as DCStatusExt,
} from "double-counting/types"

const statusToVariant: Record<DCStatusExt, BadgeProps["severity"]> = {
  [DCStatusExt.ACCEPTED]: "success",
  [DCStatusExt.INPROGRESS]: "info",
  [DCStatusExt.PENDING]: "info",
  [DCStatusExt.REJECTED]: "error",
  [DCStatusExt.EXPIRED]: "new",
  [DCStatusExt.EXPIRES_SOON]: "warning",
}

const ApplicationStatus = ({
  expirationDate,
  status,
}: {
  status: DCStatus
  expirationDate?: string
}) => {
  const { t } = useTranslation()

  let extStatus = status as unknown as DCStatusExt

  const statusLabels = {
    [DCStatusExt.PENDING]: t("En attente"),
    [DCStatusExt.INPROGRESS]: t("En attente"),
    [DCStatusExt.ACCEPTED]: t("Acceptée"),
    [DCStatusExt.REJECTED]: t("Refusée"),
    [DCStatusExt.EXPIRED]: t("Expirée"),
    [DCStatusExt.EXPIRES_SOON]: t("À renouveler"),
  }

  if (expirationDate && extStatus !== DCStatusExt.REJECTED) {
    const expirationDateFormated = new Date(expirationDate)
    if (expirationDateFormated < new Date()) {
      extStatus = DCStatusExt.EXPIRED
    } else {
      const ENDING_MONTH_DELAY = 6
      const expires_soon_date = new Date(expirationDate)
      expires_soon_date.setMonth(
        expires_soon_date.getMonth() - ENDING_MONTH_DELAY
      )
      if (expires_soon_date < new Date()) {
        extStatus = DCStatusExt.EXPIRES_SOON
      }
    }
  }

  return (
    <Badge severity={statusToVariant[extStatus]}>
      {statusLabels[extStatus]}
    </Badge>
  )
}

export default ApplicationStatus
