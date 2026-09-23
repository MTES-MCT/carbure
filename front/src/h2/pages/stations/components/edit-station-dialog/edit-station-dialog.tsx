import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Portal } from "common/components/portal"
import { useTranslation } from "react-i18next"
import {
  StationForm,
  H2StationFormData,
  validateStationData,
} from "../station-form"
import useEntity from "common/hooks/entity"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { useDeleteStation, useUpdateStation } from "./edit-station-dialog.hooks"
import { H2Station } from "h2/types"

type EditStationDialogProps = {
  station: H2Station
  onClose: () => void
}

export const EditStationDialog = ({
  station,
  onClose,
}: EditStationDialogProps) => {
  const { t } = useTranslation()

  const entity = useEntity()
  const { canWriteStations } = useH2Permissions()

  const updateStation = useUpdateStation({ onClose })
  const deleteStation = useDeleteStation({ station, onClose })

  function onSubmit(form: H2StationFormData | undefined) {
    if (form) {
      const validated = validateStationData(form)
      if (validated) updateStation.execute(entity.id, station.id, validated)
    }
  }

  return (
    <Portal>
      <Dialog
        size="medium"
        onClose={onClose}
        header={
          <Dialog.Title>
            {t("Station")} {station.name}
          </Dialog.Title>
        }
        footer={
          <>
            {canWriteStations && (
              <Button customPriority="danger" onClick={deleteStation}>
                {t("Supprimer")}
              </Button>
            )}

            {canWriteStations && (
              <Button
                type="submit"
                loading={updateStation.loading}
                nativeButtonProps={{ form: "station-form" }}
              >
                {t("Sauvegarder")}
              </Button>
            )}
          </>
        }
      >
        <StationForm
          readOnly={!canWriteStations}
          station={station}
          onSubmit={onSubmit}
        />
      </Dialog>
    </Portal>
  )
}
