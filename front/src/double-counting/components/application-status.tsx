import Tag, { TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"
import {
  DoubleCountingStatus as DCStatus,
  DoubleCountingExtendedStatus as DCStatusExt,
} from "double-counting/types"

const statusToVariant: Record<DCStatusExt, TagVariant> = {
  [DCStatusExt.ACCEPTED]: "success",
  [DCStatusExt.INPROGRESS]: "info",
  [DCStatusExt.PENDING]: "info",
  [DCStatusExt.REJECTED]: "danger",
  [DCStatusExt.EXPIRED]: "none",
  [DCStatusExt.EXPIRES_SOON]: "warning",
  [DCStatusExt.INCOMING]: "success",
}

const ApplicationStatus = ({
  expirationDate,
  big,
  status,
}: {
  big?: boolean
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
    [DCStatusExt.INCOMING]: t("À venir"),
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
      //  else if (extStatus === DCStatus.Accepted) {
      //   extStatus = DCStatus.Incoming
      // }
    }
  }

  return (
    <Tag big={big} variant={statusToVariant[extStatus]}>
      {statusLabels[extStatus]}
    </Tag>
  )
}

export default ApplicationStatus
