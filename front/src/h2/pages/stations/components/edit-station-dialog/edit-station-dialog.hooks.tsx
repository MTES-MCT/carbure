import { usePortal } from "common/components/portal"
import { EditStationDialog } from "./edit-station-dialog"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { t } from "i18next"
import * as api from "../../api"
import { H2Station } from "h2/types"

export function useEditStationDialog() {
  const portal = usePortal()
  return (station: H2Station) =>
    portal((onClose) => (
      <EditStationDialog station={station} onClose={onClose} />
    ))
}

export function useUpdateStation({ onClose }: { onClose: () => void }) {
  const notify = useNotify()
  const notifyError = useNotifyError()

  return useMutation(api.updateH2Station, {
    invalidates: ["h2-stations"],
    onSuccess: () => {
      notify(t("La station a bien été modifiée !"), { variant: "success" })
      onClose()
    },
    onError: (err) => {
      notifyError(err)
    },
  })
}
