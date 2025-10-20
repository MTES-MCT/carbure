import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { saveEnergy } from "./api"
import { BiomethaneEnergyInputRequest } from "./types"

export const useSaveEnergy = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const saveEnergyMutation = useMutation(
    (data: BiomethaneEnergyInputRequest) => saveEnergy(entity.id, data),
    {
      invalidates: ["energy"],
      onSuccess: () => {
        notify(t("Les données ont bien été mises à jour."), {
          variant: "success",
        })
      },
      onError: () => notifyError(),
    }
  )

  return saveEnergyMutation
}
