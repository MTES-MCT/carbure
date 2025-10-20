import { Balance, CreateOperationType } from "accounting/types"
import { ExportationDialogForm } from "./exportation-dialog.types"
import useEntity from "common/hooks/entity"
import { useCreateOperation } from "accounting/hooks/useCreateOperation.hooks"

type ExportationDialogProps = {
  balance: Balance
  values: ExportationDialogForm
  onClose: () => void
  onOperationCreated: () => void
}
export const useExportationDialog = ({
  balance,
  values,
  onClose,
  onOperationCreated,
}: ExportationDialogProps) => {
  const entity = useEntity()

  const createOperation = useCreateOperation({
    onOperationCreated,
    data: {
      type: values.country?.is_in_europe
        ? CreateOperationType.EXPEDITION
        : CreateOperationType.EXPORTATION,
      from_depot: values.from_depot?.id,
      export_recipient: values.export_recipient,
      customs_category: balance.customs_category,
      biofuel: balance.biofuel?.id ?? null,
      debited_entity: entity.id,
      lots: values.selected_lots!,
      export_country: values.country?.code_pays ?? "",
    },
    quantity: values.quantity!,
    onClose,
  })

  return createOperation
}
