import { useTranslation } from "react-i18next"

import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/use-action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import {
  ActionSiteFieldOptions,
  useActionFields,
} from "traceability/hooks/use-action-fields"
import {
  ActionIndustry,
  ActionQuery,
  ActionStatus,
  ActionType,
} from "traceability/types"
import { SiteTypeEnum } from "api-schema"
import { Text } from "common/components/text"

const H2_LOT_QUERY: Partial<ActionQuery> = {
  type: [ActionType.INIT],
  status: [ActionStatus.PENDING],
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
      excelImport={{
        buttonLabel: t("Importer des lots"),
        description: (
          <Text>
            Vous pouvez importer plusieurs lots à la fois en important un
            fichier excel à travers le champ au bas de cette fenêtre.
          </Text>
        ),
        fieldLabels: {
          lot_id: t("Id du lot"),
          producer: t("Producteur"),
          batch_id: t("N° de batch (batch ID)"),
        },
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
        columns.working_date,
        columns.pos_id,
        { ...columns.site, header: t("Station") },
        { ...columns.material, header: t("Nature d'H2") },
        columns.quantity,
      ]}
      fields={[
        fields.pos_id,
        fields.certificate,
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
      industry={ActionIndustry.H2}
    />
  )
}

export default LotsPage
