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
import { useCreateStation } from "./create-station-dialog.hooks"

type CreateStationDialogProps = {
  onClose: () => void
}

export const CreateStationDialog = ({ onClose }: CreateStationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const createStation = useCreateStation({ onClose })

  function onSubmit(form: H2StationFormData | undefined) {
    if (!form) return
    const validated = validateStationData(form)
    if (validated) createStation.execute(entity.id, validated)
  }

  return (
    <Portal>
      <Dialog
        size="medium"
        onClose={onClose}
        header={<Dialog.Title>{t("Inscrire une station")}</Dialog.Title>}
        footer={
          <Button
            type="submit"
            loading={createStation.loading}
            nativeButtonProps={{ form: "station-form" }}
          >
            {t("Inscrire la station")}
          </Button>
        }
      >
        <StationForm onSubmit={onSubmit} />
      </Dialog>
    </Portal>
  )
}
