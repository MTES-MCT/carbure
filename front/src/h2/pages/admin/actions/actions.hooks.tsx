import { useTranslation } from "react-i18next"

import { Cell } from "common/components/table2"
import { useH2LotsPage } from "h2/pages/lots/lots.hooks"
import { ActionsPageProps } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import { ActionIndustry } from "traceability/types"

type H2AdminActionsPageConfig = Pick<
  ActionsPageProps,
  | "industry"
  | "listTitle"
  | "detailTitle"
  | "subpath"
  | "fixedQuery"
  | "filters"
  | "columns"
  | "fieldsets"
>

export function useH2AdminActionsPage(): H2AdminActionsPageConfig {
  const { t } = useTranslation()
  const { page: lotsPage } = useH2LotsPage()
  const filters = useActionFilters()
  const columns = useActionColumns()

  return {
    industry: ActionIndustry.H2,
    listTitle: t("Actions"),
    detailTitle: t("Action n˚"),
    subpath: "actions",
    fixedQuery: {},
    filters: [
      filters.status,
      filters.material,
      filters.type,
      filters.site,
      { ...filters.holder, label: t("Producteur") },
      filters.period,
      filters.shipping_method,
    ],
    columns: [
      columns.status,
      columns.type,
      { ...columns.holder, header: t("Producteur") },
      {
        ...columns.material,
        cell: (action) => <Cell text={action.material?.name} />,
      },
      columns.site,
      columns.period,
      columns.pos_id,
      columns.quantity,
    ],
    fieldsets: lotsPage.fieldsets,
  }
}
