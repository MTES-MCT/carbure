import Tag, { TagVariant } from "common/components/tag"
import { useTranslation } from "react-i18next"
import { DoubleCountingExtendedStatus as DCStatus } from "double-counting/types"

const statusToVariant: Record<DCStatus, TagVariant> = {
  [DCStatus.ACCEPTED]: "success",
  [DCStatus.INPROGRESS]: "info",
  [DCStatus.PENDING]: "info",
  [DCStatus.REJECTED]: "danger",
  [DCStatus.EXPIRED]: "none",
  [DCStatus.EXPIRES_SOON]: "warning",
  [DCStatus.INCOMING]: "success",
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

  const statusLabels = {
    [DCStatus.PENDING]: t("En attente"),
    [DCStatus.INPROGRESS]: t("En attente"),
    [DCStatus.ACCEPTED]: t("Acceptée"),
    [DCStatus.REJECTED]: t("Refusée"),
    [DCStatus.EXPIRED]: t("Expirée"),
    [DCStatus.EXPIRES_SOON]: t("À renouveller"),
    [DCStatus.INCOMING]: t("À venir"),
  }

  if (expirationDate && status !== DCStatus.REJECTED) {
    const expirationDateFormated = new Date(expirationDate)
    if (expirationDateFormated < new Date()) {
      status = DCStatus.EXPIRED
    } else {
      const ENDING_MONTH_DELAY = 6
      const expires_soon_date = new Date(expirationDate)
      expires_soon_date.setMonth(
        expires_soon_date.getMonth() - ENDING_MONTH_DELAY
      )
      if (expires_soon_date < new Date()) {
        status = DCStatus.EXPIRES_SOON
      }
      //  else if (status === DCStatus.Accepted) {
      //   status = DCStatus.Incoming
      // }
    }
  }

  return (
    <Tag big={big} variant={statusToVariant[status]}>
      {statusLabels[status]}
    </Tag>
  )
}

export default ApplicationStatus
