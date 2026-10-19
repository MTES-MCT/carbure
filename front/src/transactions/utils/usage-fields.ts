import { DeliveryType, FuelUsage } from "transactions/types"

type UsageFields = {
  delivery_type?: DeliveryType | string
  usage?: FuelUsage
  usage_precision?: string
}

export function hasUsageFields(deliveryType?: DeliveryType | string): boolean {
  return (
    deliveryType === DeliveryType.RFC || deliveryType === DeliveryType.Direct
  )
}

export function normalizeUsageFields<T extends UsageFields>(value: T): T {
  const normalized = { ...value }

  if (!hasUsageFields(normalized.delivery_type)) {
    normalized.usage = undefined
    normalized.usage_precision = undefined
  } else if (normalized.usage !== FuelUsage.Other) {
    normalized.usage_precision = undefined
  }

  return normalized
}
