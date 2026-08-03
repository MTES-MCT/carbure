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
  const canWrite = entity.canWrite()

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
            {canWrite && (
              <Button customPriority="danger" onClick={deleteStation}>
                {t("Supprimer")}
              </Button>
            )}

            {canWrite && (
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
          readOnly={!canWrite}
          station={station}
          onSubmit={onSubmit}
        />
      </Dialog>
    </Portal>
  )
}
