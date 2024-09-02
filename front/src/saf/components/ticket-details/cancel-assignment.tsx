import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Cross, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafTicket } from "saf/types"
import * as api from "../../pages/operator/api"
import TicketTag from "../tickets/tag"

interface CancelAssignmentProps {
  ticket: SafTicket
  onClose: () => void
}

export const CancelAssignment = ({
  ticket,
  onClose,
}: CancelAssignmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const cancelSafTicket = useMutation(api.cancelSafTicket, {
    invalidates: [
      "ticket-source-details",
      "tickets",
      "operator-snapshot",
      "ticket-sources",
    ],
  })

  const cancelTicket = async () => {
    await cancelSafTicket.execute(entity.id, ticket.id)
    notify(
      t("Le ticket a été annulé et son volume peut être à nouveau affecté."),
      { variant: "success" }
    )
    onClose()
  }

  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
        <header>
          <TicketTag status={ticket.status} />
          <h1>
            {t("Annuler le ticket n°")}
            {ticket?.carbure_id ?? "..."}
          </h1>
        </header>

        <main>
          <section>
            <p>
              <strong>
                {t("Êtes-vous sûr de vouloir annuler ce ticket ?")}
              </strong>
            </p>
            <p>
              {t(
                "Cela entrainera sa suppression et les quantités seront à nouveau disponible pour  être affectées."
              )}
            </p>
          </section>
        </main>

        <footer>
          <Button
            icon={Cross}
            label={t("Annuler l'affectation")}
            variant="danger"
            action={cancelTicket}
          />

          <Button icon={Return} label={t("Retour")} action={onClose} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default CancelAssignment
