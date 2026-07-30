import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Portal } from "common/components/portal"
import { Trans, useTranslation } from "react-i18next"
import {
  StationForm,
  H2StationFormData,
  validateStationData,
} from "../station-form"
import { Checkbox } from "common/components/inputs2"
import { useState } from "react"
import { useMutation } from "common/hooks/async"
import * as api from "../../api"
import useEntity from "common/hooks/entity"
import { useNotify, useNotifyError } from "common/components/notifications"

type CreateStationDialogProps = {
  onClose: () => void
}

export const CreateStationDialog = ({ onClose }: CreateStationDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const notify = useNotify()
  const notifyError = useNotifyError()

  const [confirmed, setConfirmed] = useState(false)

  const createStation = useMutation(api.createStation, {
    onSuccess: () => {
      notify(t("La station a bien été créée !"), { variant: "success" })
      onClose()
    },
    onError: (err) => {
      notifyError(err)
    },
  })

  function onSubmit(form: H2StationFormData | undefined) {
    if (form && confirmed) {
      const validated = validateStationData(form)
      if (validated) createStation.execute(validated, entity.id)
    }
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
            disabled={!confirmed}
            nativeButtonProps={{ form: "station-form" }}
          >
            {t("Inscrire la station")}
          </Button>
        }
      >
        <StationForm onSubmit={onSubmit} />

        <Checkbox
          value={confirmed}
          onChange={setConfirmed}
          label={
            <span>
              <Trans>
                En cochant cette case, je déclare sur l’honneur que les
                instruments de mesure de la masse d'H2 sont conformes au{" "}
                <a
                  href="https://www.legifrance.gouv.fr/jorf/id/JORFTEXT000000579193"
                  target="_blank"
                >
                  Décret no 2001-387
                </a>{" "}
                du 3 mai 2001 relatif au contrôle des instruments de mesure
              </Trans>
            </span>
          }
        />
      </Dialog>
    </Portal>
  )
}
