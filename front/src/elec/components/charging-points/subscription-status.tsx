import { useTranslation } from "react-i18next"
import Tag, { TagVariant } from "common/components/tag"
import { ElecChargingPointsSubscriptionStatus } from "elec/types"

const statusToVariant: Record<ElecChargingPointsSubscriptionStatus, TagVariant> = {
  [ElecChargingPointsSubscriptionStatus.Accepted]: "success",
  [ElecChargingPointsSubscriptionStatus.Pending]: "info",
  [ElecChargingPointsSubscriptionStatus.Rejected]: "danger",
}

const SubscriptionStatus = ({
  big,
  status,
}: {
  big?: boolean
  status: ElecChargingPointsSubscriptionStatus
}) => {
  const { t } = useTranslation()

  const statusLabels = {
    [ElecChargingPointsSubscriptionStatus.Pending]: t("En attente"),
    [ElecChargingPointsSubscriptionStatus.Accepted]: t("Accepté"),
    [ElecChargingPointsSubscriptionStatus.Rejected]: t("Refusé"),
  }

  return (
    <Tag big={big} variant={statusToVariant[status]}>
      {statusLabels[status]}
    </Tag>
  )
}

export default SubscriptionStatus
