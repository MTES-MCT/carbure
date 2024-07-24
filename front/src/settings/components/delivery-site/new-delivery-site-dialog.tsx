import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Edit, Return } from "common/components/icons"
import { PortalInstance } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { DeliverySiteForm, DeliverySiteFormType } from "./delivery-site-form"
import * as api from "../../api/delivery-sites"
import { useNotify } from "common/components/notifications"

type NewDeliverySiteDialogProps = {
  onClose: PortalInstance["close"]
}

export const NewDeliverySiteDialog = ({
  onClose,
}: NewDeliverySiteDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const addDeliverySite = useMutation(api.addDeliverySite, {
    onSuccess: () => {
      notify(t("Votre demande d'ajout de dépôt a bien été prise en compte !"), {
        variant: "success",
      })
    },
    onError: () => {
      notify(t("Une erreur est survenue lors de l'ajout de votre dépôt."), {
        variant: "danger",
      })
    },
  })

  const handleSubmit = (values: DeliverySiteFormType) => {
    // addDeliverySite.execute()
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
          loading={addDeliverySite.loading}
          icon={Edit}
          label={t("Valider")}
          submit="new-delivery-site"
        />
        <Button asideX icon={Return} action={onClose} label={t("Retour")} />
      </footer>
    </Dialog>
  )
}
