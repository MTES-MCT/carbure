import { useTranslation } from "react-i18next"

import { useActionFields } from "traceability/hooks/action-fields"
import {
  ActionIndustry,
  ActionQuery,
  ActionStatus,
  ActionType,
} from "traceability/types"
import { ActionsPageProps } from "traceability/components/actions-page"
import { EmptyCertificates } from "./components/empty-certificates"
import { TransferCertificateDialog } from "./components/transfer-certificate-dialog"
import { Button } from "common/components/button2"
import { compact } from "common/utils/collection"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { usePortal } from "common/components/portal"
import { useH2ActionColumns } from "h2/hooks/use-h2-action-columns"
import { useH2ActionFilters } from "h2/hooks/use-h2-action-filters"

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
  | "tabs"
  | "emptyState"
  | "filters"
  | "columns"
  | "fieldsets"
  | "renderQuantityTotal"
>

export function useH2CertificatesPage(): {
  page: H2CertificatesPageConfig
} {
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

  return {
    page: {
      industry: ActionIndustry.H2,
      listTitle: t("Certificats d'hydrogène"),
      detailTitle: t("Certificat d'hydrogène n˚"),
      subpath: "certificates",
      fixedQuery: H2_CERTIFICATE_QUERY,
      tabs: [
        {
          key: "available",
          label: t("Disponibles"),
          query: {
            status: [ActionStatus.CREATED],
            quantity_available: true,
          },
          columns: compact([
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
          key: "transferred",
          label: t("En attente"),
          query: {
            type: [ActionType.TRANSFER],
            status: [ActionStatus.PENDING],
          },
          columns: [
            ...sharedColumns,
            columns.quantity,
            {
              ...columns.holder,
              header: t("Redevable"),
            },
          ],
          filters: [
            {
              ...filters.holder,
              label: t("Redevable"),
            },
            ...sharedFilters,
          ],
        },
      ],
      emptyState: <EmptyCertificates />,
      filters: sharedFilters,
      columns: sharedColumns,
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
