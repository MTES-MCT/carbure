import i18next from "i18next"

import { DecimalInput } from "common/components/inputs2"
import { ReadOnlyValue } from "common/components/inputs2/base-input"
import { formatUnit, getStepFromFractionDigits } from "common/utils/formatters"
import type { ActionField } from "./use-action-fields"
import {
  ACTION_CONVERTED_QUANTITY,
  ActionQuantityKey,
} from "traceability/utils/quantities"

const ACTION_DECIMAL_STEP = getStepFromFractionDigits(3)

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
            {...props}
            {...form.bind("quantity")}
          />
        )
      }

      const value = form.value[key]

      return (
        <ReadOnlyValue
          label={props.label}
          readOnly
          value={
            value
              ? formatUnit(Number(value), ACTION_CONVERTED_QUANTITY[key], {
                  fractionDigits: 3,
                })
              : ""
          }
        />
      )
    },
  }
}
