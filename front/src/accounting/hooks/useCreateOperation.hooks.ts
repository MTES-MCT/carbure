import {
  createOperation,
  CreateOperationProps,
} from "accounting/api/biofuels/operations"
import useEntity from "common/hooks/entity"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"
import { useMutation } from "common/hooks/async"
import { useCallback } from "react"
import { CreateOperationType, OperationsStatus } from "accounting/types"

export type UseCreateOperationProps = {
  onOperationCreated: () => void
  data: CreateOperationProps
  quantity: number
  onClose: () => void
}
export const useCreateOperation = ({
  onOperationCreated,
  data,
  quantity,
  onClose,
}: UseCreateOperationProps) => {
  const entity = useEntity()
  const notify = useNotify()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  const getSuccessMessage = useCallback(
    (operationType: CreateOperationType, quantity: number) => {
      const quantityFormatted = formatUnit(quantity, {
        fractionDigits: 0,
      })
      const messages: Partial<Record<CreateOperationType, string>> = {
        [CreateOperationType.TRANSFERT]: t(
          "Le transfert de droits d'une quantité de {{quantity}} a été réalisé avec succès",
          { quantity: quantityFormatted }
        ),
        [CreateOperationType.EXPORTATION]: t(
          "L'exportation d'une quantité de {{quantity}} a été réalisée avec succès",
          { quantity: quantityFormatted }
        ),
      }

      if (!messages[operationType]) {
        return t("L'opération a été réalisée avec succès")
      }

      return messages[operationType]
    },
    [formatUnit, t]
  )
  return useMutation(
    ({ draft }: { draft?: boolean } = {}) =>
      createOperation(entity.id, {
        ...data,
        status: draft ? OperationsStatus.DRAFT : undefined,
      }),
    {
      invalidates: ["balances"],
      onSuccess: ({ data: operation }) => {
        onOperationCreated()
        const message =
          operation?.status === OperationsStatus.DRAFT
            ? t("L'opération a été enregistrée en tant que brouillon.")
            : getSuccessMessage(data.type, quantity)

        notify(message, { variant: "success" })
        onClose()
      },
      onError: () => {
        notify(
          t("Une erreur est survenue lors de la création de l'opération"),
          {
            variant: "danger",
          }
        )
      },
    }
  )
}
