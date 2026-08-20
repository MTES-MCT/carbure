import { useTranslation } from "react-i18next"

import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/use-action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import { useActionFields } from "traceability/hooks/use-action-fields"
import { ActionIndustry, ActionQuery, ActionType } from "traceability/types"

const H2_LOT_QUERY: Partial<ActionQuery> = {
  industry: [ActionIndustry.H2],
  type: [ActionType.INIT],
}

const LotsPage = () => {
  const { t } = useTranslation()

  const filters = useActionFilters()
  const columns = useActionColumns()

  const fields = useActionFields()

  return (
    <ActionsPage
      listTitle={t("Lots d'hydrogène")}
      detailTitle={t("Lot d'hydrogène n˚")}
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
      fields={[
        fields.pos_id,
        fields.holder,
        { ...fields.material, label: t("Nature d'hydrogène") },
        fields.quantity,
        fields.site,
        fields.shipping_date,
        fields.shipping_distance,
        fields.shipping_method,
        fields.ei,
        fields.ep,
        fields.etd,
        fields.eu,
        fields.eccs,
      ]}
    />
  )
}

export default LotsPage
