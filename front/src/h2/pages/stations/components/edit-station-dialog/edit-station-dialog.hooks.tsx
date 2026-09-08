import { usePortal } from "common/components/portal"
import { EditStationDialog } from "./edit-station-dialog"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { t } from "i18next"
import * as api from "../../api"
import { H2Station } from "h2/types"
import { Confirm } from "common/components/dialog2"
import useEntity from "common/hooks/entity"

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

export function useDeleteStation({
  station,
  onClose,
}: {
  station: H2Station
  onClose: () => void
}) {
  const portal = usePortal()
  const notify = useNotify()
  const notifyError = useNotifyError()

  const entity = useEntity()

  const deleteStation = useMutation(api.deleteH2Station, {
    invalidates: ["h2-stations"],
    onSuccess: () => {
      notify(t("La station a bien été supprimée !"), { variant: "success" })
      onClose()
    },
    onError: (err) => {
      notifyError(err)
    },
  })

  return () =>
    portal((close) => (
      <Confirm
        title={t("Supprimer la station")}
        description={t("Voulez vous supprimer la station {{name}} ?", {
          name: station.name,
        })}
        confirm={t("Supprimer")}
        icon="ri-close-line"
        customVariant="danger"
        onConfirm={() => deleteStation.execute(entity.id, station.id)}
        onClose={close}
        hideCancel
      />
    ))
}
