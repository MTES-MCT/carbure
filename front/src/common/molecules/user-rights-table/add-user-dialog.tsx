import Dialog, { Confirm } from "common/components/dialog"
import Form from "common/components/form"
import { type PortalInstance } from "common/components/portal"
import { useTranslation } from "react-i18next"

type AddUserDialogProps = {
  onClose: PortalInstance["close"]
}

export const AddUserDialog = ({ onClose }: AddUserDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Ajouter un utilisateur")}</h1>
      </header>
      <main>
        <section>{t("Veuillez remplir les informations suivantes")}</section>
        <section>
          <Form id="access-right" onSubmit={() => {}}>
            form content
          </Form>
        </section>
      </main>
    </Dialog>
  )
}
