import { usePortal } from "common/components/portal"
import { CreateStationDialog } from "./create-station-dialog"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { t } from "i18next"
import * as api from "../../api"

export function useCreateStationDialog() {
  const portal = usePortal()
  return () => portal((onClose) => <CreateStationDialog onClose={onClose} />)
}

export function useCreateStation({ onClose }: { onClose: () => void }) {
  const notify = useNotify()
  const notifyError = useNotifyError()

  return useMutation(api.createH2Station, {
    invalidates: ["h2-stations"],
    onSuccess: () => {
      notify(t("La station a bien été créée !"), { variant: "success" })
      onClose()
    },
    onError: (err) => {
      notifyError(err)
    },
  })
}
