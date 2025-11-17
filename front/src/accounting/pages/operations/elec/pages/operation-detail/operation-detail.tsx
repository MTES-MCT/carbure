import Dialog from "common/components/dialog2/dialog"
import Portal from "common/components/portal"
import { useQuery } from "common/hooks/async"
import { useNavigate } from "react-router-dom"
import * as api from "accounting/api/elec/operations"
import useEntity from "common/hooks/entity"
import { useHashMatch } from "common/components/hash-route"
import {
  getOperationEntity,
  getOperationQuantity,
  isSendingOperation,
} from "../../operations.utils"
import { OperationBadge } from "accounting/components/operation-badge"
import css from "../../../operations.module.css"
import { Text } from "common/components/text"
import { Trans, useTranslation } from "react-i18next"
import { Grid, LoaderOverlay, Main } from "common/components/scaffold"
import { formatDate, formatNumber } from "common/utils/formatters"
import { compact } from "common/utils/collection"
import { Button } from "common/components/button2"
import {
  useAcceptOperation,
  useDeleteOperation,
  useRejectOperation,
} from "./operation-detail.hooks"
import { Unit, UserRole } from "common/types"
import { useUnit } from "common/hooks/unit"
import { formatOperationType } from "accounting/utils/formatters"
import { ElecOperationsStatus, ElecOperationType } from "accounting/types"

export const OperationDetail = () => {
  const navigate = useNavigate()
  const entity = useEntity()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
  const match = useHashMatch("operation/:id")

  const { result, loading } = useQuery(api.getOperationDetail, {
    key: "operation-detail",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const operation = result?.data
  const canUpdateOperation =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const { execute: deleteOperation, loading: deleteOperationLoading } =
    useDeleteOperation({
      operation,
      onDeleteOperation: closeDialog,
    })

  const { execute: acceptOperation, loading: acceptOperationLoading } =
    useAcceptOperation({
      operation,
      onAcceptOperation: closeDialog,
    })

  const { execute: rejectOperation, loading: rejectOperationLoading } =
    useRejectOperation({
      operation,
      onRejectOperation: closeDialog,
    })

  const fields = operation
    ? compact([
        {
          label: t("Date d'opération"),
          value: formatDate(operation?.created_at),
        },
        {
          label: t("Quantité"),
          value: `${getOperationQuantity(
            operation,
            formatUnit(operation.quantity ?? 0, {
              unit: Unit.MJ,
            })
          )}`,
        },
        {
          label: t("Tonnes CO2 eq evitées"),
          value: formatNumber(operation.avoided_emissions, {
            fractionDigits: 0,
          }),
        },
        operation.type === ElecOperationType.ACQUISITION && {
          label: t("Expéditeur"),
          value: getOperationEntity(operation)?.name ?? "-",
        },
        operation.type === ElecOperationType.CESSION && {
          label: t("Destinataire"),
          value: getOperationEntity(operation)?.name ?? "-",
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
            {operation?.type === ElecOperationType.ACQUISITION &&
              operation?.status === ElecOperationsStatus.PENDING &&
              canUpdateOperation && (
                <>
                  <Button
                    customPriority="danger"
                    iconId="fr-icon-close-line"
                    onClick={() => {
                      rejectOperation(entity.id, operation.id)
                    }}
                    loading={rejectOperationLoading}
                  >
                    {t("Refuser")}
                  </Button>
                  <Button
                    customPriority="success"
                    iconId="fr-icon-check-line"
                    nativeButtonProps={{ form: "patch-operation" }}
                    loading={acceptOperationLoading}
                    onClick={() => {
                      acceptOperation(entity.id, operation.id)
                    }}
                  >
                    {t("Accepter")}
                  </Button>
                </>
              )}
            {isSendingOperation(operation?.type ?? "") &&
              operation?.status === ElecOperationsStatus.PENDING &&
              canUpdateOperation && (
                <Button
                  customPriority="danger"
                  iconId="fr-icon-close-line"
                  onClick={() => deleteOperation(entity.id, operation.id)}
                  loading={deleteOperationLoading}
                >
                  {operation?.type === ElecOperationType.CESSION &&
                    t("Annuler le certificat de cession")}
                  {operation?.type === ElecOperationType.TENEUR &&
                    t("Annuler le certificat de teneur")}
                </Button>
              )}
          </>
        }
      >
        <Main>
          {loading ? (
            <LoaderOverlay />
          ) : (
            <>
              <Grid className={css["operation-detail-fields"]}>
                {fields.map(({ label, value }) => (
                  <div key={label}>
                    <Text className={css["field-label"]}>{label}</Text>
                    <Text className={css["field-value"]}>{value}</Text>
                  </div>
                ))}
              </Grid>
              {operation?.type === ElecOperationType.ACQUISITION &&
                operation?.status === ElecOperationsStatus.PENDING &&
                canUpdateOperation && (
                  <>
                    <Text>{t("Voulez-vous accepter ce certificat ?")}</Text>
                    <div>
                      <Text>
                        <Trans defaults="<b>Si vous l’acceptez</b>, celui-ci sera comptabilisé en acquisition et viendra alimenter votre solde." />
                      </Text>
                      <Text>
                        <Trans defaults="Si vous le <b>refusez</b>, celui-ci n’apparaîtra plus dans vos opérations en attente." />
                      </Text>
                    </div>
                  </>
                )}
              {operation?.type === ElecOperationType.CESSION &&
                operation?.status === ElecOperationsStatus.PENDING &&
                canUpdateOperation && (
                  <>
                    <Text>
                      {t("Voulez-vous annuler ce certificat de cession ?")}
                    </Text>
                    <Text>
                      {t(
                        "Vous pouvez annuler un certificat de cession, tant que celui-ci est encore en attente côté redevable."
                      )}
                    </Text>
                  </>
                )}
            </>
          )}
        </Main>
      </Dialog>
    </Portal>
  )
}
