import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Edit, Return } from "common/components/icons"
import { PortalInstance, useCloseAllPortals } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import {
  DeliverySiteForm,
  DeliverySiteFormType,
} from "./create-delivery-site-form"
import * as api from "../../api/delivery-sites"
import { useNotify } from "common/components/notifications"
import useEntity from "carbure/hooks/entity"

type CreateDeliverySiteDialogProps = {
  onClose: PortalInstance["close"]
}

export const CreateDeliverySiteDialog = ({
  onClose,
}: CreateDeliverySiteDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const closeAll = useCloseAllPortals()
  const createNewDeliverySite = useMutation(api.createNewDeliverySite, {
    invalidates: ["production-sites"],
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
    onError: () => {
      notify(t("Une erreur est survenue lors de l'ajout de votre dépôt."), {
        variant: "danger",
      })
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
      values.blender,
      values.ownership_type,
      values.blending_is_outsourced,
      values.electrical_efficiency!,
      values.thermal_efficiency!,
      values.useful_temperature!
    )
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Créer un nouveau dépôt")}</h1>
      </header>

      <main>
        <section>
          <p>{t("Veuillez remplir les informations suivantes :")}</p>
        </section>
        <section>
          <DeliverySiteForm
            onCreate={handleSubmit}
            formId="new-delivery-site"
          />
        </section>
      </main>
      <footer>
        <Button
          variant="primary"
          loading={createNewDeliverySite.loading}
          icon={Edit}
          label={t("Valider")}
          submit="new-delivery-site"
        />
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}
