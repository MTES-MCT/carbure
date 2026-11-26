import { useTranslation } from "react-i18next"

import { Badge } from "@codegouvfr/react-dsfr/Badge"
import { Button } from "common/components/button2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { Row } from "common/components/scaffold"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { Unit } from "common/types"
import { compact } from "common/utils/collection"
import { useH2ActionColumns } from "h2/hooks/use-h2-action-columns"
import { useH2ActionFilters } from "h2/hooks/use-h2-action-filters"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { TransferCertificateDialog } from "h2/pages/certificates/components/transfer-certificate-dialog"
import { createAction } from "traceability/api"
import {
  ActionsPageProps,
  QUERY_KEY,
} from "traceability/components/actions-page"
import { useActionFields } from "traceability/hooks/action-fields"
import {
  Action,
  ActionIndustry,
  ActionQuery,
  ActionStatus,
  ActionType,
} from "traceability/types"
import { formatUnitActionDecimal } from "traceability/utils/formatters"

const HELD_VOLUME_QUERY: Partial<ActionQuery> = {
  type: [ActionType.TRANSFER],
  status: [ActionStatus.ACCEPTED],
  held: true,
}

function today() {
  const date = new Date()
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")
  return `${date.getFullYear()}-${month}-${day}`
}

type LiableVolumesPageConfig = Pick<
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

export function useLiableVolumesPage(): { page: LiableVolumesPageConfig } {
  const { t } = useTranslation()
  const filters = useH2ActionFilters()
  const columns = useH2ActionColumns()
  const fields = useActionFields()
  const { canValidateCertificates } = useH2Permissions()

  const sharedColumns = [
    { ...columns.carbure_id, header: t("N˚ d'identifiant Carbure") },
    columns.previous_material,
    columns.period,
    columns.total_emissions,
    columns.quantity_available,
  ]
  const sharedFilters = [filters.period, filters.previous_material]
  const availability = {
    header: t("Statut"),
    cell: (action: Action) => <LiableVolumeStatus action={action} />,
  }

  return {
    page: {
      industry: ActionIndustry.H2,
      listTitle: t("Volumes H2"),
      detailTitle: t("Volume d'hydrogène n˚"),
      subpath: "liable-volumes",
      fixedQuery: HELD_VOLUME_QUERY,
      tabs: [
        {
          key: "available",
          label: t("Disponible"),
          query: { quantity_available: true },
          columns: compact([
            availability,
            ...sharedColumns,
            canValidateCertificates && {
              header: t("Actions"),
              cell: (action) => <VolumeActions action={action} />,
            },
          ]),
        },
        {
          key: "history",
          label: t("Historique"),
          query: { quantity_available: false },
          columns: sharedColumns,
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
            { ...fields.quantity, label: t("Quantité") },
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

const LiableVolumeStatus = ({ action }: { action: Action }) => {
  const { t } = useTranslation()
  const intact = Number(action.quantity_available) === Number(action.quantity)

  return (
    <Badge severity={intact ? "success" : "warning"}>
      {intact ? t("Disponible") : t("Entamé")}
    </Badge>
  )
}

const VolumeActions = ({ action }: { action: Action }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const portal = usePortal()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const consume = useMutation(createAction, {
    invalidates: [QUERY_KEY],
    onSuccess: () => {
      notify(t("Le volume a été consommé."), { variant: "success" })
    },
    onError: (err) => notifyError(err),
  })

  return (
    <Row gap="md">
      <Button
        captive
        title={t("Céder")}
        priority="secondary"
        iconId="ri-send-plane-line"
        size="small"
        onClick={() =>
          portal((close) => (
            <TransferCertificateDialog onClose={close} action={action} />
          ))
        }
      />
      <Button
        captive
        title={t("Consommer")}
        priority="primary"
        iconId="ri-fire-line"
        size="small"
        loading={consume.loading}
        onClick={() =>
          consume.execute(entity.id, action.industry, {
            type: ActionType.CONSUME,
            status: ActionStatus.CREATED,
            holder: entity.id,
            parent: action.id,
            quantity: action.quantity_available,
            working_date: today(),
          })
        }
      />
    </Row>
  )
}
