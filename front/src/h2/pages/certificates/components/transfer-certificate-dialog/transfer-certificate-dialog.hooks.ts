import { useTranslation } from "react-i18next"

import { useForm } from "common/components/form2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useRoutes } from "common/hooks/routes"
import { EntityPreview } from "common/types"
import { createAction } from "traceability/api"
import { QUERY_KEY } from "traceability/components/actions-page"
import { Action, ActionStatus, ActionType } from "traceability/types"

export type TransferCertificateForm = {
  quantity?: string
  holder?: EntityPreview
}

const CURRENT_YEAR = new Date().getFullYear()

function co2Quantity(
  quantity: string | undefined,
  emissions: string | null | undefined
) {
  const quantityValue = Number(quantity)
  const emissionsValue = Number(emissions)
  if (
    !quantity ||
    !Number.isFinite(quantityValue) ||
    !Number.isFinite(emissionsValue)
  ) {
    return ""
  }
  return (quantityValue * emissionsValue).toFixed(3)
}

export function useTransferCertificateDialog(
  action: Action,
  onClose: () => void
) {
  const { t } = useTranslation()
  const routes = useRoutes()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const form = useForm<TransferCertificateForm>({ quantity: "" })
  const parent = action.parent
  const previousMaterial = action.inherited_fields.previous_material
  const year = parent?.working_date
    ? new Date(parent.working_date).getFullYear()
    : CURRENT_YEAR

  const emission = useMutation(createAction, {
    invalidates: [QUERY_KEY],
    onSuccess: () => {
      notify(t("Le certificat de cession a bien été envoyé."), {
        variant: "success",
      })
      onClose()
    },
    onError: (err) => notifyError(err),
  })

  const transfer = (value: TransferCertificateForm | undefined) => {
    if (!value?.holder || !value.quantity) return

    emission.execute(entity.id, action.industry, {
      type: ActionType.TRANSFER,
      status: ActionStatus.PENDING,
      holder: value.holder.id,
      parent: action.id,
      quantity: value.quantity,
      pos_id: "demoo",
    })
  }

  return {
    form,
    transfer,
    loading: emission.loading,
    parent,
    previousMaterial,
    unit: previousMaterial?.unit,
    lotPath: parent ? routes.HYDROGEN(year).LOT(parent.id) : undefined,
    co2: co2Quantity(form.value.quantity, action.total_emissions?.total),
    setMaxQuantity: () => form.setField("quantity", action.quantity_available),
  }
}
