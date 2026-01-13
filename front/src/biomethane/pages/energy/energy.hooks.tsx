import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { saveEnergy } from "./api"
import { BiomethaneEnergyInputRequest } from "./types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export const useSaveEnergy = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { currentAnnualDeclarationKey, selectedYear } = useAnnualDeclaration()

  const saveEnergyMutation = useMutation(
    (data: BiomethaneEnergyInputRequest) =>
      saveEnergy(entity.id, selectedYear, data),
    {
      invalidates: ["energy", currentAnnualDeclarationKey],
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
