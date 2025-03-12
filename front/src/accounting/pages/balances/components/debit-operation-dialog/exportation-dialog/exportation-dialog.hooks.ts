import { Balance, CreateOperationType } from "accounting/types"
import { ExportationDialogForm } from "./exportation-dialog.types"
import useEntity from "common/hooks/entity"
import { useNotify } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"
import { createOperation, simulate } from "accounting/api"
import { useMutation } from "common/hooks/async"

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
  const notify = useNotify()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

  const onSubmit = () => {
    return simulate(entity.id, {
      customs_category: balance.customs_category,
      biofuel: balance.biofuel?.id ?? null,
      debited_entity: entity.id,
      target_volume: values.quantity!,
      target_emission: values.avoided_emissions!,
    }).then((response) => {
      const lots = response.data?.selected_lots
      if (lots) {
        return createOperation(entity.id, {
          lots: lots.map(({ lot_id, ...rest }) => ({
            id: lot_id,
            ...rest,
          })),
          biofuel: balance.biofuel?.id ?? null,
          customs_category: balance.customs_category,
          debited_entity: entity.id,
          type: CreateOperationType.EXPORTATION,
          from_depot: values.from_depot?.id,
          to_depot: values.to_depot?.id,
          credited_entity: values.credited_entity?.id,
          export_country: values.country?.name,
        })
      }
    })
  }

  return useMutation(onSubmit, {
    invalidates: ["balances"],
    onSuccess: () => {
      onClose()
      onOperationCreated()
      notify(
        t(
          "L'exportation d'une quantité de {{quantity}} a été réalisée avec succès",
          {
            quantity: formatUnit(values.quantity!, 0),
          }
        ),
        { variant: "success" }
      )
    },
    onError: () => {
      notify(t("Une erreur est survenue lors de l'exportation"), {
        variant: "danger",
      })
    },
  })
}
