import { useTranslation } from "react-i18next"

import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/use-action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import { ActionIndustry, ActionQuery, ActionType } from "traceability/types"

const H2_LOT_QUERY: Partial<ActionQuery> = {
  industry: [ActionIndustry.H2],
  type: [ActionType.INIT],
}

const LotsPage = () => {
  const { t } = useTranslation()

  const columns = useActionColumns()
  const filters = useActionFilters()

  return (
    <ActionsPage
      title={t("Lots")}
      subpath="lots"
      fixedQuery={H2_LOT_QUERY}
      filters={[
        { ...filters.material, label: t("Nature d'H2") },
        filters.site,
        filters.shipping_method,
      ]}
      columns={[
        columns.id,
        columns.holder,
        columns.industry,
        { ...columns.material, header: t("Nature d'H2") },
        columns.quantity,
        { ...columns.site, header: t("Station") },
      ]}
    />
  )
}

export default LotsPage
