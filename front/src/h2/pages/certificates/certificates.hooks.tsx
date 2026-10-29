import { useTranslation } from "react-i18next"

import { useActionColumns } from "traceability/hooks/action-columns"
import { useActionFilters } from "traceability/hooks/use-action-filters"
import { useActionFields } from "traceability/hooks/action-fields"
import { ActionIndustry, ActionQuery, ActionType } from "traceability/types"
import { ActionsPageProps } from "traceability/components/actions-page"
import { EmptyCertificates } from "./components/empty-certificates"

const H2_CERTIFICATE_QUERY: Partial<ActionQuery> = {
  type: [ActionType.VALORIZE],
}

type H2CertificatesPageConfig = Pick<
  ActionsPageProps,
  | "industry"
  | "listTitle"
  | "detailTitle"
  | "subpath"
  | "fixedQuery"
  | "emptyState"
  | "filters"
  | "columns"
  | "fieldsets"
>

export function useH2CertificatesPage(): {
  page: H2CertificatesPageConfig
} {
  const { t } = useTranslation()

  const filters = useActionFilters()
  const columns = useActionColumns()
  const fields = useActionFields()

  return {
    page: {
      industry: ActionIndustry.H2,
      listTitle: t("Certificats d'hydrogène"),
      detailTitle: t("Certificat d'hydrogène n˚"),
      subpath: "certificates",
      fixedQuery: H2_CERTIFICATE_QUERY,
      emptyState: <EmptyCertificates />,
      filters: [filters.period, filters.origin_material],
      columns: [
        { ...columns.carbure_id, header: t("N˚ d'identifiant Carbure") },
        columns.period,
        columns.quantity,
        columns.total_emissions,
      ],
      fieldsets: [
        {
          legend: t("Certificat"),
          fields: [
            fields.carbure_id,
            { ...fields.quantity, label: t("Quantité certifiée") },
            { ...fields.working_date, label: t("Date de création") },
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
      ],
    },
  }
}
