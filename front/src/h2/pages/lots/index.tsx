import { useTranslation } from "react-i18next"

import { ActionsPage } from "traceability/components/actions-page"
import { useActionColumns } from "traceability/hooks/action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import {
  ActionSiteFieldOptions,
  useActionFields,
} from "traceability/hooks/action-fields"
import { ActionIndustry, ActionQuery, ActionType } from "traceability/types"
import { SiteTypeEnum } from "api-schema"
import { Text } from "common/components/text"

const H2_LOT_QUERY: Partial<ActionQuery> = {
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
      industry={ActionIndustry.H2}
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
          lot_id: t("ID_LOT/Batch ID"),
          lot_quantity: t("Quantite (kg)"),
          producer: t("Producteur"),
          certificate: t("N° du certificat du producteur"),
          etd1: t("Etd1"),
          etd2: t("Etd2"),
          quantity: t("Quantité consommée (kg)"),
          working_date: t("Mois d'utilisation / consommation"),
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
        filters.period,
        filters.site,
        filters.shipping_method,
      ]}
      columns={[
        columns.status,
        columns.working_date,
        columns.pos_id,
        { ...columns.site, header: t("Station") },
        { ...columns.material, header: t("Nature d'H2") },
        columns.mass,
        columns.total_emissions,
      ]}
      fieldsets={[
        {
          legend: t("Production"),
          fields: [
            fields.certificate,
            { ...fields.material, label: t("Nature d'hydrogène") },
            fields.pos_id,
          ],
        },
        {
          legend: t("Transport"),
          fields: [
            fields.shipping_method,
            fields.shipping_distance,
            fields.shipping_date,
          ],
        },
        {
          legend: t("Consommation"),
          fields: [
            {
              ...fields.site,
              label: t("Station"),
              options: H2_SITE_FIELD_OPTIONS,
            },
            { ...fields.mass, label: t("Quantité consommée") },
            { ...fields.working_date, label: t("Date de consommation") },
          ],
        },
        {
          legend: t("Émissions/réductions"),
          fields: [
            fields.ei,
            fields.ep,
            fields.etd,
            fields.eu,
            fields.eccs,
            fields.total_emissions,
          ],
        },
      ]}
    />
  )
}

export default LotsPage
