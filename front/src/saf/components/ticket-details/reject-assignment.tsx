import useEntity from "common/hooks/entity"
import { EntityType } from "common/types"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Form from "common/components/form"
import { Cross, Return } from "common/components/icons"
import { TextInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { SafTicket } from "saf/types"
import TicketTag from "../tickets/tag"
import { rejectSafAirlineTicket } from "saf/pages/airline/api"
import { rejectSafOperatorTicket } from "saf/pages/operator/api"

interface RejectAssignmentProps {
  ticket: SafTicket
  onClose: () => void
}

export const RejectAssignment = ({
  ticket,
  onClose,
}: RejectAssignmentProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const [comment, setComment] = useState<string | undefined>()

  const rejectSafTicket = useMutation(
    entity.entity_type === EntityType.Airline
      ? rejectSafAirlineTicket
      : rejectSafOperatorTicket,
    {
      invalidates: [
        "ticket-details",
        "airline-snapshot",
        "operator-snapshot",
        "tickets",
        `nav-stats-${entity.id}`,
      ],
      onSuccess: () => ticketRejected(),
    }
  )

  const ticketRejected = () => {
    notify(
      t(
        "Le ticket a été refusé et la raison mentionnée a été communiquée au fournisseur."
      ),
      { variant: "success" }
    )
    onClose()
  }

  const rejectTicket = async () => {
    //TO TEST comment below and add ticketRejected()
    await rejectSafTicket.execute(entity.id, ticket.id, comment!)
  }

  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
        <header>
          <TicketTag status={ticket.status} />
          <h1>
            {t("Refuser le ticket n°")}
            {ticket?.carbure_id ?? "..."}
          </h1>
        </header>

        <main>
          <section>
            <p>
              <strong>
                {t("Pour quelle raison refusez-vous ce ticket ?")}
              </strong>{" "}
              {t(
                "Cela entraînera la suppression du ticket. Le producteur sera notifié de votre refus."
              )}
            </p>
            <Form id="reject-ticket" onSubmit={rejectTicket}>
              <TextInput
                value={comment}
                label={t("Commentaire")}
                onChange={setComment}
                required
                placeholder={t("Entrez un commentaire...")}
              />
            </Form>
          </section>
        </main>

        <footer>
          <Button
            icon={Cross}
            label={t("Refuser l'affectation")}
            variant="danger"
            submit="reject-ticket"
          />

          <Button icon={Return} label={t("Retour")} action={onClose} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default RejectAssignment
