import i18next from "i18next"

import { Cell } from "common/components/table2"
import { formatUnitOnly } from "common/utils/formatters"
import { formatActionDecimal } from "traceability/utils/formatters"
import {
  ActionQuantityKey,
  getActionQuantity,
} from "traceability/utils/quantities"
import { ActionColumn } from "./use-action-columns"

export function quantityColumn(
  key: ActionQuantityKey = "quantity"
): ActionColumn {
  return {
    key,
    header: i18next.t("Quantité"),
    cell: (action) => {
      const { value, unit } = getActionQuantity(action, key)
      const text = formatActionDecimal(value)

      return (
        <Cell
          text={text || "-"}
          sub={text ? formatUnitOnly(unit) : undefined}
        />
      )
    },
  }
}
