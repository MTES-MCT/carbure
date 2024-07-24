import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Edit, Return } from "common/components/icons"
import { PortalInstance, useCloseAllPortals } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { DeliverySiteForm, DeliverySiteFormType } from "./delivery-site-form"
import * as api from "../../api/delivery-sites"
import { useNotify } from "common/components/notifications"
import useEntity from "carbure/hooks/entity"

type NewDeliverySiteDialogProps = {
  onClose: PortalInstance["close"]
}

export const NewDeliverySiteDialog = ({
  onClose,
}: NewDeliverySiteDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const closeAll = useCloseAllPortals()
  const createNewDeliverySite = useMutation(api.createNewDeliverySite, {
    onSuccess: () => {
      closeAll()
      notify(
        t(
          "Votre demande d'ajout de dépôt a bien été prise en compte ! Vous serez notifié lorsque celle-ci aura été traitée."
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
      values.depot_id!,
      values.depot_type!,
      values.address!,
      values.postal_code!,
      values.ownership_type!,
      values.blending_outsourced,
      values.blending_entity
    )
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajouter un dépôt")}</h1>
      </header>

      <main>
        <section>
          <p>{t("Veuillez remplir les informations suivantes :")}</p>
        </section>
        <section>
          <DeliverySiteForm
            onSubmit={handleSubmit}
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
