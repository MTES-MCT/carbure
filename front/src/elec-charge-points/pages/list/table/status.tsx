import Tag, { TagVariant } from "common/components/tag"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { useStatusLabels } from "../index.hooks"
import { ChargePointStatus } from "../types"

type ChargePointsListTableStatusProps = {
  status: ChargePointStatus
}

const statusToVariant: Record<ChargePointStatus, TagVariant> = {
  [ChargePointStatus.Pending]: "info",
  [ChargePointStatus.AuditInProgress]: "warning",
  [ChargePointStatus.Accepted]: "success",
}

export const ChargePointsListTableStatus = ({
  status,
}: ChargePointsListTableStatusProps) => {
  const { t } = useTranslation()

  const statusLabels = useStatusLabels()

  return (
    <Tag big variant={!status ? "none" : statusToVariant[status]}>
      {statusLabels[status]}
    </Tag>
  )
}
