import Dialog from "common/components/dialog2/dialog"
import Portal, { usePortal } from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { useNavigate } from "react-router-dom"
import * as api from "./api"
import useEntity from "carbure/hooks/entity"
import { useHashMatch } from "common/components/hash-route"
import {
  formatOperationType,
  formatSector,
  getOperationEntity,
  getOperationVolume,
} from "material-accounting/operations/operations.utils"
import { OperationBadge } from "material-accounting/operations/components/operation-badge"
import css from "./operation-detail.module.css"
import { Text } from "common/components/text"
import { useTranslation } from "react-i18next"
import { Grid } from "common/components/scaffold"
import { formatDate } from "common/utils/formatters"
import { compact } from "common/utils/collection"
import { Button } from "common/components/button2"
import {
  OperationsStatus,
  OperationType,
} from "material-accounting/operations/types"
import { DeleteOperationDialog } from "./components/delete-operation-dialog"

export const OperationDetail = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const { t } = useTranslation()
  const match = useHashMatch("operation/:id")
  const portal = usePortal()

  const { result } = useQuery(api.getOperationDetail, {
    key: "operation-detail",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const operation = result?.data

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const openDialogDeleteOperation = () => {
    if (!operation) return

    portal((close) => (
      <DeleteOperationDialog
        onClose={close}
        operation={operation}
        onDeleteOperation={closeDialog}
      />
    ))
  }

  const fields = operation
    ? compact([
        {
          label: t("Date d'opération"),
          value: formatDate(operation?.created_at),
        },
        {
          label: t("Expéditeur"),
          value: getOperationEntity(operation)?.name ?? "-",
        },
        {
          label: t("Transaction"),
          value: formatOperationType(operation.type),
        },
        { label: t("Filière"), value: formatSector(operation.sector) },
        { label: t("Catégorie"), value: operation.customs_category },
        { label: t("Biocarburant"), value: operation.biofuel },
        {
          label: t("Volume"),
          value: getOperationVolume(operation),
        },
        { label: t("Tonnes CO2 eq evitées"), value: "???" },
        {
          label: t("Dépôt expéditeur"),
          value: operation.from_depot?.name ?? "-",
        },
      ])
    : []

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={
          operation && (
            <div className={css["operation-detail-header"]}>
              <Dialog.Title>
                {formatOperationType(operation.type)} n°{operation.id}
              </Dialog.Title>
              <OperationBadge status={operation.status} />
            </div>
          )
        }
        footer={
          <>
            {operation?.type === OperationType.ACQUISITION &&
              operation?.status === OperationsStatus.PENDING && (
                <>
                  <Button customPriority="danger" iconId="fr-icon-close-line">
                    {t("Refuser")}
                  </Button>
                  <Button customPriority="success" iconId="fr-icon-check-line">
                    {t("Accepter")}
                  </Button>
                </>
              )}
            {operation?.type === OperationType.CESSION &&
              operation?.status === OperationsStatus.PENDING && (
                <Button
                  customPriority="danger"
                  iconId="fr-icon-close-line"
                  onClick={openDialogDeleteOperation}
                >
                  {t("Annuler le certificat de cession")}
                </Button>
              )}
            {(operation?.status === OperationsStatus.ACCEPTED ||
              operation?.status === OperationsStatus.REJECTED) && (
              <Button priority="secondary" onClick={closeDialog}>
                {t("Annuler")}
              </Button>
            )}
          </>
        }
      >
        <Grid className={css["operation-detail-fields"]}>
          {fields.map(({ label, value }) => (
            <div key={label}>
              <Text className={css["field-label"]}>{label}</Text>
              <Text className={css["field-value"]}>{value}</Text>
            </div>
          ))}
        </Grid>
      </Dialog>
    </Portal>
  )
}
