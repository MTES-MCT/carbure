import i18next from "i18next"

import { DecimalInput } from "common/components/inputs2"
import { getStepFromFractionDigits } from "common/utils/formatters"
import type { ActionField } from "./use-action-fields"
import {
  ACTION_CONVERTED_QUANTITY,
  ActionQuantityKey,
} from "traceability/utils/quantities"
import { formatUnitActionDecimal } from "traceability/utils/formatters"

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
            readOnlyValue={
              form.value.material?.unit
                ? formatUnitActionDecimal(
                    form.value.quantity,
                    form.value.material?.unit
                  )
                : "-"
            }
            {...props}
            {...form.bind("quantity")}
          />
        )
      }

      return (
        <DecimalInput
          {...props}
          step={ACTION_DECIMAL_STEP}
          readOnlyValue={formatUnitActionDecimal(
            form.value[key],
            ACTION_CONVERTED_QUANTITY[key]
          )}
          readOnly
          value={form.value[key] ?? ""}
        />
      )
    },
  }
}
