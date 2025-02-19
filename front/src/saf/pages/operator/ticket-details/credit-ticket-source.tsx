import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafTicket } from "saf/types"
import * as api from "../api"

interface CreditTicketSourceProps {
  ticket: SafTicket
  onClose: () => void
  onCredit: () => void
}

export const CreditTicketSource = ({
  ticket,
  onClose,
  onCredit,
}: CreditTicketSourceProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const creditSafTicketSource = useMutation(api.creditSafTicketSource, {
    invalidates: ["ticket-sources", "tickets", "operator-snapshot"],
  })

  const ticketSourceCredited = () => {
    notify(
      t("Le volume de ce ticket est désormais dans vos volumes disponibles !"),
      { variant: "success" }
    )
    onClose()
    onCredit()
  }

  const creditTicketSource = async () => {
    await creditSafTicketSource.execute(entity.id, ticket.id)
    ticketSourceCredited()
  }

  return (
    <Portal onClose={onClose}>
      <Dialog
        onClose={onClose}
        header={
          <Dialog.Title>
            {t("Accepter et créditer mes volumes disponibles ?")}
          </Dialog.Title>
        }
        footer={
          <Button
            iconId="ri-send-plane-line"
            priority="primary"
            onClick={creditTicketSource}
          >
            {t("Accepter et créditer")}
          </Button>
        }
      >
        <p>
          {t(
            "En acceptant ce ticket, vous déverserez le volume de ce ticket parmi vos volumes disponibles de Carburant d'Aviation Durable, afin de pouvoir l'affecter à un autre client. Ce ticket restera visible dans votre historique."
          )}
        </p>
      </Dialog>
    </Portal>
  )
}

export default CreditTicketSource
