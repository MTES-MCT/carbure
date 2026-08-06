import { DeliveryType, FuelUsage } from "transactions/types"

type UsageFields = {
  delivery_type?: DeliveryType | string
  usage?: FuelUsage
  usage_precision?: string
}

export function normalizeUsageFields<T extends UsageFields>(value: T): T {
  const normalized = { ...value }

  if (normalized.delivery_type !== DeliveryType.RFC) {
    normalized.usage = undefined
    normalized.usage_precision = undefined
  } else if (normalized.usage !== FuelUsage.Other) {
    normalized.usage_precision = undefined
  }

  return normalized
}
