import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { PortalInstance, useCloseAllPortals } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import {
  DeliverySiteForm,
  DeliverySiteFormType,
} from "./create-delivery-site-form"
import * as api from "../../api/delivery-sites"
import { useNotify, useNotifyError } from "common/components/notifications"
import useEntity from "common/hooks/entity"

type CreateDeliverySiteDialogProps = {
  onClose: PortalInstance["close"]
}

export const CreateDeliverySiteDialog = ({
  onClose,
}: CreateDeliverySiteDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const entity = useEntity()
  const closeAll = useCloseAllPortals()
  const createNewDeliverySite = useMutation(api.createNewDeliverySite, {
    invalidates: ["delivery-sites"],
    onSuccess: () => {
      closeAll()
      notify(
        t(
          "Votre demande d'ajout de dépôt a bien été prise en compte ! Vous serez notifié par mail lorsque celle-ci aura été traitée."
        ),
        {
          variant: "success",
        }
      )
    },
    onError: (e) => {
      notifyError(e)
    },
  })

  const handleSubmit = (values: DeliverySiteFormType) => {
    createNewDeliverySite.execute(
      entity.id,
      values.name!,
      values.city!,
      values.country!,
      values.customs_id!,
      values.site_type!,
      values.address!,
      values.postal_code!,
      values.blender!,
      values.ownership_type!,
      values.blending_is_outsourced!,
      values.electrical_efficiency!,
      values.thermal_efficiency!,
      values.useful_temperature!
    )
  }

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Créer un nouveau dépôt")}</Dialog.Title>}
      footer={
        <Button
          loading={createNewDeliverySite.loading}
          iconId="ri-pencil-line"
          type="submit"
          nativeButtonProps={{
            form: "new-delivery-site",
          }}
        >
          {t("Valider")}
        </Button>
      }
      size="medium"
    >
      <p>{t("Veuillez remplir les informations suivantes :")}</p>

      <DeliverySiteForm onCreate={handleSubmit} formId="new-delivery-site" />
    </Dialog>
  )
}
