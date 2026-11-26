import { useTranslation } from "react-i18next"

import { Unit } from "common/types"
import { useH2ActionColumns } from "h2/hooks/use-h2-action-columns"
import { useH2ActionFilters } from "h2/hooks/use-h2-action-filters"
import { ActionsPageProps } from "traceability/components/actions-page"
import { useActionFields } from "traceability/hooks/action-fields"
import {
  ActionIndustry,
  ActionQuery,
  ActionStatus,
  ActionType,
} from "traceability/types"
import { formatUnitActionDecimal } from "traceability/utils/formatters"

const H2_SENT_QUERY: Partial<ActionQuery> = {
  type: [ActionType.TRANSFER],
}

type H2SentCertificatesPageConfig = Pick<
  ActionsPageProps,
  | "industry"
  | "listTitle"
  | "detailTitle"
  | "subpath"
  | "fixedQuery"
  | "tabs"
  | "filters"
  | "columns"
  | "fieldsets"
  | "renderQuantityTotal"
>

export function useH2SentCertificatesPage(): {
  page: H2SentCertificatesPageConfig
} {
  const { t } = useTranslation()

  const filters = useH2ActionFilters()
  const columns = useH2ActionColumns()
  const fields = useActionFields()

  const sharedColumns = [
    { ...columns.carbure_id, header: t("N˚ d'identifiant Carbure") },
    columns.previous_material,
    columns.period,
    columns.total_emissions,
    columns.quantity,
    { ...columns.holder, header: t("Redevable") },
  ]
  const sharedFilters = [
    { ...filters.holder, label: t("Redevable") },
    filters.period,
    filters.previous_material,
  ]

  return {
    page: {
      industry: ActionIndustry.H2,
      listTitle: t("Certificats envoyés"),
      detailTitle: t("Certificat envoyé n˚"),
      subpath: "sent-certificates",
      fixedQuery: H2_SENT_QUERY,
      tabs: [
        {
          key: "pending",
          label: t("En attente"),
          query: { status: [ActionStatus.PENDING] },
        },
        {
          key: "accepted",
          label: t("Acceptés"),
          query: { status: [ActionStatus.ACCEPTED] },
        },
        {
          key: "rejected",
          label: t("Refusés"),
          query: { status: [ActionStatus.REJECTED] },
        },
      ],
      filters: sharedFilters,
      columns: sharedColumns,
      renderQuantityTotal: (count, total) =>
        t("{{count}} certificats pour un total de {{total}}", {
          count,
          total: formatUnitActionDecimal(total ?? 0, Unit.kg),
        }),
      fieldsets: [
        {
          legend: t("Cession"),
          fields: [
            fields.carbure_id,
            { ...fields.holder, label: t("Redevable") },
            { ...fields.quantity, label: t("Quantité cédée") },
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
