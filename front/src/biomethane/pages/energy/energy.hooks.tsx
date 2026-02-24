import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { saveEnergy } from "./api"
import { BiomethaneEnergyInputRequest } from "./types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { useMemo } from "react"

export const useSaveEnergy = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { annualDeclarationKey, selectedYear } = useAnnualDeclaration()

  const saveEnergyMutation = useMutation(
    (data: BiomethaneEnergyInputRequest) =>
      saveEnergy(entity.id, selectedYear, data),
    {
      invalidates: ["energy", annualDeclarationKey],
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

export const useDisplayConditionalSectionsEnergy = () => {
  const { isDeclarationInCurrentPeriod, annualDeclaration } =
    useAnnualDeclaration()

  return useMemo(() => {
    // If the declaration year selected is not the current year and the declaration is open, we don't display the conditional sections
    if (!isDeclarationInCurrentPeriod && annualDeclaration?.is_open)
      return false

    return true
  }, [isDeclarationInCurrentPeriod, annualDeclaration?.is_open])
}
