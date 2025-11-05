import useEntity from "common/hooks/entity"
import { TransfertDialogForm } from "./transfert-dialog.types"
import { Balance, CreateOperationType } from "accounting/types"
import { useCreateOperation } from "accounting/hooks/useCreateOperation.hooks"

type TransfertDialogProps = {
  balance: Balance
  values: TransfertDialogForm
  onClose: () => void
  onOperationCreated: () => void
}

export const useTransfertDialog = ({
  balance,
  values,
  onClose,
  onOperationCreated,
}: TransfertDialogProps) => {
  const entity = useEntity()

  const createOperation = useCreateOperation({
    onOperationCreated,
    data: {
      type: CreateOperationType.TRANSFERT,
      credited_entity: values.credited_entity?.id,
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
