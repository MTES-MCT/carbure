import useEntity from "common/hooks/entity"
import { DevaluationDialogForm } from "./devaluation-dialog.types"
import { Balance, CreateOperationType } from "accounting/types"
import { useCreateOperation } from "accounting/hooks/useCreateOperation.hooks"

type DevaluationDialogProps = {
  balance: Balance
  values: DevaluationDialogForm
  onClose: () => void
  onOperationCreated: () => void
}

export const useDevaluationDialog = ({
  balance,
  values,
  onClose,
  onOperationCreated,
}: DevaluationDialogProps) => {
  const entity = useEntity()

  const createOperation = useCreateOperation({
    onOperationCreated,
    data: {
      type: CreateOperationType.DEVALUATION,
      from_depot: values.from_depot?.id,
      devaluation_type: values.devaluation_type,
      customs_category: balance.customs_category,
      biofuel: balance.biofuel?.id ?? null,
      debited_entity: entity.id,
      lots: values.selected_lots!,
    },
    quantity: values.quantity!,
    onClose,
  })

  return createOperation
}
