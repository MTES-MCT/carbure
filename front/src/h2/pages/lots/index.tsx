import { useTranslation } from "react-i18next"

import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/use-action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import {
  ActionSiteFieldOptions,
  useActionFields,
} from "traceability/hooks/use-action-fields"
import { ActionIndustry, ActionQuery, ActionType } from "traceability/types"
import { SiteTypeEnum } from "api-schema"

const H2_LOT_QUERY: Partial<ActionQuery> = {
  industry: [ActionIndustry.H2],
  type: [ActionType.INIT],
}

const H2_SITE_FIELD_OPTIONS: ActionSiteFieldOptions = {
  siteTypes: [SiteTypeEnum.H2_REFUELING_STATION],
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
      mainAction={{
        icon: "fr-icon-add-line",
        label: t("Importer des lots d'hydrogène"),
        onAction: () => {},
      }}
      detailActions={[
        {
          icon: "fr-icon-close-line",
          label: "Supprimer",
          variant: "danger",
          onAction: () => {},
        },
      ]}
      filters={[
        { ...filters.material, label: t("Nature d'H2") },
        filters.site,
        filters.shipping_method,
      ]}
      columns={[
        { ...columns.material, header: t("Nature d'H2") },
        columns.quantity,
        { ...columns.site, header: t("Station") },
        columns.holder,
      ]}
      fields={[
        fields.pos_id,
        fields.holder,
        { ...fields.material, label: t("Nature d'hydrogène") },
        fields.quantity,
        { ...fields.site, label: t("Station"), options: H2_SITE_FIELD_OPTIONS },
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
