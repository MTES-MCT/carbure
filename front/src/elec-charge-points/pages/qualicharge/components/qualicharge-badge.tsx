import { Badge, BadgeProps } from "@codegouvfr/react-dsfr/Badge"
import { formatQualichargeStatus } from "../formatters"
import { QualichargeValidatedBy } from "../types"

export const QualichargeBadge = ({
  status,
}: {
  status: QualichargeValidatedBy | undefined
}) => {
  const labelMapping: Record<QualichargeValidatedBy, BadgeProps["severity"]> = {
    [QualichargeValidatedBy.BOTH]: "success",
    [QualichargeValidatedBy.CPO]: "info",
    [QualichargeValidatedBy.DGEC]: "info",
    [QualichargeValidatedBy.NO_ONE]: "info",
  }

  if (!status) return null

  return (
    <Badge severity={labelMapping[status]} noIcon>
      {formatQualichargeStatus(status)}
    </Badge>
  )
}
