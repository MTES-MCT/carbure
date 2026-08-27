import { formatNumber } from "common/utils/formatters"

export function formatActionDecimal(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return ""
  return formatNumber(Number(value), { fractionDigits: 3 })
}
