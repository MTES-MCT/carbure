import { Trans, useTranslation } from "react-i18next"
import { EntityDepot } from "common/types"
import Button from "common/components/button"
import { Return } from "common/components/icons"
import { Dialog } from "common/components/dialog"
import { DeliverySiteForm } from "./create-delivery-site-form"

type DeliverySiteDialogProps = {
  deliverySite: EntityDepot
  onClose: () => void
}

export const DeliverySiteDialog = ({
  deliverySite,
  onClose,
}: DeliverySiteDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Détails du dépôt")}</h1>
      </header>

      <main>
        <section>
          <DeliverySiteForm
            formId="new-delivery-site"
            isReadOnly
            deliverySite={deliverySite}
          />
        </section>
      </main>

      <footer>
        <Button asideX icon={Return} action={onClose}>
          <Trans>Retour</Trans>
        </Button>
      </footer>
    </Dialog>
  )
}
