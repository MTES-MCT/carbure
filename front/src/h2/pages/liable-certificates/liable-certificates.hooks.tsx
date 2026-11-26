import { useTranslation } from "react-i18next"

import { Button } from "common/components/button2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { Row } from "common/components/scaffold"
import { Cell } from "common/components/table2"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { Unit } from "common/types"
import { compact } from "common/utils/collection"
import { useH2ActionColumns } from "h2/hooks/use-h2-action-columns"
import { useH2ActionFilters } from "h2/hooks/use-h2-action-filters"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { updateActionStatus } from "traceability/api"
import {
  ActionsPageProps,
  QUERY_KEY,
} from "traceability/components/actions-page"
import { useActionFields } from "traceability/hooks/action-fields"
import {
  Action,
  ActionIndustry,
  ActionStatus,
  ActionType,
} from "traceability/types"
import { formatUnitActionDecimal } from "traceability/utils/formatters"

type LiableCertificatesPageConfig = Pick<
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

export function useLiableCertificatesPage(): {
  page: LiableCertificatesPageConfig
} {
  const { t } = useTranslation()
  const filters = useH2ActionFilters()
  const columns = useH2ActionColumns()
  const fields = useActionFields()
  const { canValidateCertificates } = useH2Permissions()

  const sharedColumns = [
    columns.status,
    { ...columns.carbure_id, header: t("N˚ d'identifiant Carbure") },
    columns.previous_material,
    columns.period,
    columns.total_emissions,
    columns.quantity,
  ]
  const sharedFilters = [filters.period, filters.previous_material]
  const sender = {
    header: t("Expéditeur"),
    cell: (action: Action) => <Cell text={action.parent?.holder.name} />,
  }
  const recipient = { ...columns.holder, header: t("Destinataire") }

  return {
    page: {
      industry: ActionIndustry.H2,
      listTitle: t("Certificats"),
      detailTitle: t("Certificat n˚"),
      subpath: "liable-certificates",
      fixedQuery: {},
      tabs: [
        {
          key: "received",
          label: t("Reçus"),
          query: { type: [ActionType.TRANSFER], held: true },
          columns: compact([
            ...sharedColumns,
            sender,
            canValidateCertificates && {
              header: t("Actions"),
              cell: (action) =>
                action.status === ActionStatus.PENDING ? (
                  <DecisionButtons action={action} />
                ) : null,
            },
          ]),
          filters: sharedFilters,
        },
        {
          key: "sent",
          label: t("Envoyés"),
          query: { type: [ActionType.TRANSFER], held: false },
          columns: [...sharedColumns, recipient],
          filters: [
            { ...filters.holder, label: t("Destinataire") },
            ...sharedFilters,
          ],
        },
        {
          key: "consumed",
          label: t("Consommés"),
          query: { type: [ActionType.CONSUME], held: true },
          columns: sharedColumns,
          filters: sharedFilters,
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
          legend: t("Certificat"),
          fields: [
            fields.carbure_id,
            { ...fields.holder, label: t("Détenteur") },
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

const DecisionButtons = ({ action }: { action: Action }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const decision = useMutation(updateActionStatus, {
    invalidates: [QUERY_KEY],
    onSuccess: () => {
      notify(t("Le certificat a été mis à jour."), { variant: "success" })
    },
    onError: (err) => notifyError(err),
  })

  return (
    <Row gap="md">
      <Button
        captive
        title={t("Refuser")}
        priority="secondary"
        iconId="ri-close-line"
        size="small"
        disabled={decision.loading}
        onClick={() =>
          decision.execute(
            entity.id,
            action.id,
            action.industry,
            ActionStatus.REJECTED
          )
        }
      />
      <Button
        captive
        title={t("Accepter")}
        priority="primary"
        iconId="ri-check-line"
        size="small"
        disabled={decision.loading}
        onClick={() =>
          decision.execute(
            entity.id,
            action.id,
            action.industry,
            ActionStatus.ACCEPTED
          )
        }
      />
    </Row>
  )
}
