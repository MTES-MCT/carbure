import i18next from "i18next"

import { DecimalInput } from "common/components/inputs2"
import {
  formatUnitOnly,
  getStepFromFractionDigits,
} from "common/utils/formatters"
import type { ActionField } from "./use-action-fields"
import {
  ACTION_CONVERTED_QUANTITY,
  ActionQuantityKey,
} from "traceability/utils/quantities"

const ACTION_DECIMAL_FRACTION_DIGITS = 3
const ACTION_DECIMAL_STEP = getStepFromFractionDigits(
  ACTION_DECIMAL_FRACTION_DIGITS
)

export function quantityField(
  key: ActionQuantityKey = "quantity"
): ActionField {
  return {
    key,
    label: i18next.t("Quantité"),
    field: ({ form, props }) => {
      if (key === "quantity") {
        return (
          <DecimalInput
            step={ACTION_DECIMAL_STEP}
            fractionDigits={ACTION_DECIMAL_FRACTION_DIGITS}
            unit={form.value.unit ? formatUnitOnly(form.value.unit) : undefined}
            {...props}
            {...form.bind("quantity")}
          />
        )
      }

      return (
        <DecimalInput
          step={ACTION_DECIMAL_STEP}
          fractionDigits={ACTION_DECIMAL_FRACTION_DIGITS}
          unit={formatUnitOnly(ACTION_CONVERTED_QUANTITY[key])}
          {...props}
          readOnly
          value={form.value[key] ?? ""}
        />
      )
    },
  }
}
