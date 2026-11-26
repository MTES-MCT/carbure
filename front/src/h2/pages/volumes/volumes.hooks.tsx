import { useTranslation } from "react-i18next"

import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { Unit } from "common/types"
import { compact } from "common/utils/collection"
import { useH2ActionColumns } from "h2/hooks/use-h2-action-columns"
import { useH2ActionFilters } from "h2/hooks/use-h2-action-filters"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { TransferCertificateDialog } from "h2/pages/certificates/components/transfer-certificate-dialog"
import { ActionsPageProps } from "traceability/components/actions-page"
import { useActionFields } from "traceability/hooks/action-fields"
import {
  ActionIndustry,
  ActionQuery,
  ActionStatus,
  ActionType,
} from "traceability/types"
import { formatUnitActionDecimal } from "traceability/utils/formatters"

import { VolumeAvailabilityBadge } from "./components/volume-availability-badge"

const H2_VOLUME_QUERY: Partial<ActionQuery> = {
  type: [ActionType.VALORIZE],
}

type H2VolumesPageConfig = Pick<
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

export function useH2VolumesPage(): { page: H2VolumesPageConfig } {
  const { t } = useTranslation()

  const filters = useH2ActionFilters()
  const columns = useH2ActionColumns()
  const fields = useActionFields()
  const { canValidateCertificates } = useH2Permissions()
  const portal = usePortal()

  const sharedColumns = [
    { ...columns.carbure_id, header: t("N˚ d'identifiant Carbure") },
    columns.previous_material,
    columns.period,
    columns.total_emissions,
  ]
  const sharedFilters = [filters.period, filters.previous_material]
  const availability = {
    header: t("Statut"),
    cell: () => <VolumeAvailabilityBadge />,
  }

  return {
    page: {
      industry: ActionIndustry.H2,
      listTitle: t("Volumes H2"),
      detailTitle: t("Volume d'hydrogène n˚"),
      subpath: "volumes",
      fixedQuery: H2_VOLUME_QUERY,
      tabs: [
        {
          key: "available",
          label: t("Disponibles"),
          query: {
            status: [ActionStatus.CREATED],
            quantity_available: true,
          },
          columns: compact([
            availability,
            ...sharedColumns,
            columns.quantity_available,
            canValidateCertificates && {
              header: t("Actions"),
              cell: (action) => (
                <Button
                  captive
                  title={t("Céder")}
                  priority="secondary"
                  iconId="ri-send-plane-line"
                  size="small"
                  onClick={() =>
                    portal((close) => (
                      <TransferCertificateDialog
                        onClose={close}
                        action={action}
                      />
                    ))
                  }
                />
              ),
            },
          ]),
        },
        {
          key: "history",
          label: t("Historique"),
          query: {
            status: [ActionStatus.CREATED],
            quantity_available: false,
          },
          columns: [...sharedColumns, columns.quantity_available],
        },
      ],
      filters: sharedFilters,
      columns: sharedColumns,
      renderQuantityTotal: (count, total) =>
        t("{{count}} volumes pour un total de {{total}}", {
          count,
          total: formatUnitActionDecimal(total ?? 0, Unit.kg),
        }),
      fieldsets: [
        {
          legend: t("Volume"),
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
