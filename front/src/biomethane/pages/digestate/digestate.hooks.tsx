import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"
import useEntity from "common/hooks/entity"
import { saveDigestate } from "./api"
import { BiomethaneDigestateInputRequest } from "./types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export const useSaveDigestate = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { selectedYear, annualDeclarationKey } = useAnnualDeclaration()

  const saveDigestateMutation = useMutation(
    (data: BiomethaneDigestateInputRequest) =>
      saveDigestate(entity.id, selectedYear, data),
    {
      invalidates: ["digestate", annualDeclarationKey],
      onSuccess: () => {
        notify(t("Le digestat a bien été mis à jour."), { variant: "success" })
      },
      onError: () => notifyError(),
    }
  )

  return saveDigestateMutation
}
