import { AccessType } from "h2/types"
import { formatAccessType } from "./formatters"
import { Normalizer } from "common/utils/normalize"

export const normalizeAccessType: Normalizer<AccessType> = (
  accessType: AccessType
) => ({
  value: accessType,
  label: formatAccessType(accessType),
})
