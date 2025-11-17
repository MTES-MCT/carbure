import { Operation, OperationsStatus, OperationType } from "accounting/types"

import useEntity from "common/hooks/entity"
import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import {
  useAcceptOperation,
  useDeleteOperation,
  useRejectOperation,
  useValidateDraftTransfer,
} from "./operation-detail-actions.hooks"
import { useMemo } from "react"
import { getOperationValidationButtonText } from "./operation-detail-actions.utils"
import {
  isReceivingOperation,
  isSendingOperation,
} from "../../../operations.utils"

export const OperationDetailActions = ({
  operation,
  closeDialog,
}: {
  operation?: Operation
  closeDialog: () => void
}) => {
  const entity = useEntity()
  const { t } = useTranslation()
  const canUpdateOperation = entity.canWrite()

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
  } = useValidateDraftTransfer({
    onSuccess: closeDialog,
  })

  const { execute: acceptOperation, loading: acceptOperationLoading } =
    useAcceptOperation({
      operation,
      onAcceptOperation: closeDialog,
    })

  const buttonsComponent = useMemo(() => {
    if (!operation || !canUpdateOperation) return []

    const buttons: React.ReactNode[] = []

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
    canUpdateOperation,
  ])

  if (!operation || !canUpdateOperation) return null

  return buttonsComponent
}
