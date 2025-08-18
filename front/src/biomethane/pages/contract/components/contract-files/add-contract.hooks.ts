import { saveContract } from "biomethane/api"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useTranslation } from "react-i18next"

export const useAddContract = ({ onSuccess }: { onSuccess?: () => void }) => {
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()
  const entity = useEntity()

  const mutation = useMutation((data) => saveContract(entity.id, data), {
    invalidates: ["contract-infos"],
    onSuccess: () => {
      notify(t("Le contrat a bien été mis à jour."), { variant: "success" })
      onSuccess?.()
    },
    onError: (e) => {
      notifyError(e)
    },
  })

  return mutation
}
