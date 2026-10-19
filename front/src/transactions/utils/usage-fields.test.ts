import { expect, it } from "vitest"
import { DeliveryType, FuelUsage } from "transactions/types"
import { normalizeUsageFields } from "./usage-fields"

it.each([DeliveryType.RFC, DeliveryType.Direct, DeliveryType.Exportation])(
  "normalizes usage fields for %s",
  (delivery_type) => {
    const relevant = delivery_type !== DeliveryType.Exportation
    const other = normalizeUsageFields({
      delivery_type,
      usage: FuelUsage.Other,
      usage_precision: "Details",
    })
    expect(other.usage).toBe(relevant ? FuelUsage.Other : undefined)
    expect(other.usage_precision).toBe(relevant ? "Details" : undefined)

    const road = normalizeUsageFields({ ...other, usage: FuelUsage.Road })
    expect(road.usage).toBe(relevant ? FuelUsage.Road : undefined)
    expect(road.usage_precision).toBeUndefined()
  }
)
