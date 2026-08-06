import { useMemo } from "react"
import { useTranslation } from "react-i18next"

import { Cell, Column } from "common/components/table2"
import { Action, ActionFilter } from "traceability/types"

import {
  ACTION_LABEL_KEYS,
  ActionColumn,
  ActionLabelOverrides,
  DEFAULT_ACTION_COLUMNS,
  DEFAULT_ACTION_FILTERS,
} from "./action-config"

const COLUMN_CELLS: Record<ActionColumn, (action: Action) => string | number> =
  {
    id: (action) => action.id,
    holder: (action) => action.holder,
    industry: (action) => action.industry,
    material: (action) => action.material,
    quantity: (action) => action.quantity,
  }

type UseActionDisplayOptions = {
  columns?: ActionColumn[]
  filters?: ActionFilter[]
  labels?: ActionLabelOverrides
}

export function useActionDisplay({
  columns = [...DEFAULT_ACTION_COLUMNS],
  filters = [...DEFAULT_ACTION_FILTERS],
  labels,
}: UseActionDisplayOptions = {}) {
  const { t } = useTranslation()

  return useMemo(() => {
    const label = (key: string) =>
      labels?.[key] ??
      (ACTION_LABEL_KEYS[key] ? t(ACTION_LABEL_KEYS[key]) : key)

    return {
      tableColumns: columns.map(
        (key): Column<Action> => ({
          key,
          header: label(key),
          cell: (action) => <Cell text={COLUMN_CELLS[key](action)} />,
        })
      ),
      filterLabels: Object.fromEntries(filters.map((key) => [key, label(key)])),
    }
  }, [columns, filters, labels, t])
}
