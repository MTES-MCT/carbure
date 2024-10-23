import Tag, { TagVariant } from "common/components/tag"
import { useStatusLabels } from "elec-charge-points/hooks/charge-point-status.hooks"
import { ChargePointStatus } from "elec-charge-points/types"

type ChargePointsListTableStatusProps = {
  status: ChargePointStatus
}

const statusToVariant: Record<ChargePointStatus, TagVariant> = {
  [ChargePointStatus.Pending]: "info",
  [ChargePointStatus.AuditInProgress]: "warning",
  [ChargePointStatus.Accepted]: "success",
}

export const ChargePointStatusTag = ({
  status,
}: ChargePointsListTableStatusProps) => {
  const statusLabels = useStatusLabels()

  return (
    <Tag big variant={!status ? "none" : statusToVariant[status]}>
      {statusLabels[status]}
    </Tag>
  )
}
