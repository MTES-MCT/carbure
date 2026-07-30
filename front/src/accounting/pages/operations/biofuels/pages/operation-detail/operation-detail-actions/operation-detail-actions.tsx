import { Operation, OperationsStatus, OperationType } from "accounting/types"

import useEntity from "common/hooks/entity"
import { useAccountingPermissions } from "accounting/hooks/use-accounting-permissions"
import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import {
  useAcceptOperation,
  useDeleteOperation,
  useRejectOperation,
  useValidateDraftOperation,
} from "./operation-detail-actions.hooks"
import { useMemo } from "react"
import { getOperationValidationButtonText } from "./operation-detail-actions.utils"
import {
  isReceivingOperation,
  isSendingOperation,
} from "../../../operations.utils"
import * as api from "accounting/api/biofuels/operations"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const OperationDetailActions = ({
  operation,
  closeDialog,
}: {
  operation?: Operation
  closeDialog: () => void
}) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const { canUpdateBiofuelOperation } = useAccountingPermissions()
  const { selectedEntityId } = useSelectedEntity()

  const { execute: deleteOperation, loading: deleteOperationLoading } =
    useDeleteOperation({
      operation,
      onDeleteOperation: closeDialog,
    })

  const { execute: rejectOperation, loading: rejectOperationLoading } =
    useRejectOperation({
      operation,
      onRejectOperation: closeDialog,
    })

  const {
    execute: validateDraftTransfer,
    loading: validateDraftTransferLoading,
  } = useValidateDraftOperation({
    operation,
    onSuccess: closeDialog,
  })

  const { execute: acceptOperation, loading: acceptOperationLoading } =
    useAcceptOperation({
      operation,
      onAcceptOperation: closeDialog,
    })

  const buttonsComponent = useMemo(() => {
    if (!operation) return []

    const buttons: React.ReactNode[] = [
      <Button
        key="export"
        iconId="fr-icon-download-fill"
        priority="secondary"
        onClick={() =>
          api.downloadOperationDetails(
            entity.id,
            operation.id,
            selectedEntityId
          )
        }
      >
        {t("Exporter")}
      </Button>,
    ]

    if (!canUpdateBiofuelOperation || entity.isAdmin) return buttons

    if (
      isReceivingOperation(operation.quantity) &&
      operation.type === OperationType.TRANSFERT &&
      operation?.status === OperationsStatus.PENDING
    ) {
      buttons.push([
        <Button
          customPriority="danger"
          iconId="fr-icon-close-line"
          onClick={() => {
            rejectOperation(entity.id, operation.id)
          }}
          loading={rejectOperationLoading}
        >
          {t("Refuser")}
        </Button>,
        <Button
          customPriority="success"
          iconId="fr-icon-check-line"
          onClick={() => {
            acceptOperation(entity.id, operation.id)
          }}
          loading={acceptOperationLoading}
          type="submit"
        >
          {t("Accepter")}
        </Button>,
      ])
    }

    if (
      isSendingOperation(operation.quantity) &&
      [OperationsStatus.PENDING, OperationsStatus.DRAFT].includes(
        operation.status!
      )
    ) {
      buttons.push(
        <Button
          customPriority="danger"
          iconId="fr-icon-close-line"
          onClick={() => deleteOperation(entity.id, operation.id)}
          loading={deleteOperationLoading}
        >
          {t("Annuler")}
        </Button>
      )
    }

    if (operation?.status === OperationsStatus.DRAFT) {
      buttons.push(
        <Button
          priority="primary"
          onClick={() =>
            validateDraftTransfer(entity.id, operation.id, {
              status: OperationsStatus.PENDING,
            })
          }
          loading={validateDraftTransferLoading}
        >
          {getOperationValidationButtonText(operation?.type as OperationType)}
        </Button>
      )
    }
    return buttons
  }, [
    operation,
    entity,
    deleteOperation,
    deleteOperationLoading,
    rejectOperation,
    rejectOperationLoading,
    validateDraftTransfer,
    validateDraftTransferLoading,
    acceptOperation,
    acceptOperationLoading,
    t,
    canUpdateBiofuelOperation,
    selectedEntityId,
  ])

  if (!operation || !canUpdateBiofuelOperation || entity.isAdmin) return null

  return buttonsComponent
}
