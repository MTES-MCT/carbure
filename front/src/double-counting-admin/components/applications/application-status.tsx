import { useTranslation } from "react-i18next"
import { DoubleCountingStatus as DCStatus } from "../../types"
import Tag, { TagVariant } from "common/components/tag"
import { el } from "date-fns/locale"

const statusToVariant: Record<DCStatus, TagVariant> = {
  [DCStatus.Accepted]: "success",
  [DCStatus.InProgress]: "info",
  [DCStatus.Pending]: "info",
  [DCStatus.Rejected]: "danger",
  [DCStatus.Expired]: "none",
  [DCStatus.ExpiresSoon]: "warning",
  [DCStatus.Incoming]: "success",
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
    [DCStatus.Pending]: t("En attente"),
    [DCStatus.InProgress]: t("En attente"),
    [DCStatus.Accepted]: t("Acceptée"),
    [DCStatus.Rejected]: t("Refusée"),
    [DCStatus.Expired]: t("Expirée"),
    [DCStatus.ExpiresSoon]: t("À renouveller"),
    [DCStatus.Incoming]: t("À venir"),
  }

  if (expirationDate && status !== DCStatus.Rejected) {
    const expirationDateFormated = new Date(expirationDate)
    if (expirationDateFormated < new Date()) {
      status = DCStatus.Expired
    } else {
      const ENDING_MONTH_DELAY = 6
      const expires_soon_date = new Date(expirationDate)
      expires_soon_date.setMonth(expires_soon_date.getMonth() - ENDING_MONTH_DELAY)
      if (expires_soon_date < new Date()) {
        status = DCStatus.ExpiresSoon
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
