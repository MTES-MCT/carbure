import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafTicket } from "saf/types"
import * as api from "../api"
import TicketTag from "../../../components/tickets/tag"

interface CancelAssignmentProps {
  ticket: SafTicket
  onClose: () => void
  onCancel: () => void
}

export const CancelAssignment = ({
  ticket,
  onClose,
  onCancel,
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
    onCancel()
  }

  return (
    <Portal onClose={onClose}>
      <Dialog
        onClose={onClose}
        header={
          <Dialog.Title>
            <TicketTag status={ticket.status} />

            {t("Annuler le ticket n°")}
            {ticket?.carbure_id ?? "..."}
          </Dialog.Title>
        }
        footer={
          <Button
            iconId="ri-close-line"
            customPriority="danger"
            onClick={cancelTicket}
            asideX
          >
            {t("Annuler l'affectation")}
          </Button>
        }
      >
        <p>
          <strong>{t("Êtes-vous sûr de vouloir annuler ce ticket ?")}</strong>
        </p>
        <p>
          {t(
            "Cela entrainera sa suppression et les quantités seront à nouveau disponible pour  être affectées."
          )}
        </p>
      </Dialog>
    </Portal>
  )
}

export default CancelAssignment
