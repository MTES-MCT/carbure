import { useTranslation } from "react-i18next"
import { useMutation, useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useNotify, useNotifyError } from "common/components/notifications"
import { getInstallation, saveInstallation } from "./api"
import { InstallationRequest } from "./types"

const INSTALLATION_QUERY_KEY = "energy-installation"

export function useEnergyInstallation() {
  const entity = useEntity()

  return useQuery(getInstallation, {
    key: INSTALLATION_QUERY_KEY,
    params: [entity.id],
  })
}

export function useSaveEnergyInstallation() {
  const entity = useEntity()
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()

  return useMutation(
    (data: InstallationRequest) => saveInstallation(entity.id, data),
    {
      invalidates: [INSTALLATION_QUERY_KEY],
      onSuccess: () =>
        notify(t("L'installation a bien été sauvegardée."), {
          variant: "success",
        }),
      onError: (error) => notifyError(error),
    }
  )
}
