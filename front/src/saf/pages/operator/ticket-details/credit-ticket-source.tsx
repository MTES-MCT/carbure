import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Return, Send } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { SafTicket } from "saf/types"
import * as api from "../api"

interface CreditTicketSourceProps {
  ticket: SafTicket
  onClose: () => void
}

export const CreditTicketSource = ({
  ticket,
  onClose,
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
  }

  const creditTicketSource = async () => {
    //TO TEST comment below and add ticketSourceCredited()
    await creditSafTicketSource.execute(entity.id, ticket.id) //TODO
    ticketSourceCredited()
  }

  return (
    <Portal onClose={onClose}>
      <Dialog onClose={onClose}>
        <header>
          <h1>{t("Accepter et créditer mes volumes disponibles ?")}</h1>
        </header>

        <main>
          <section>
            <p>
              {t(
                "En acceptant ce ticket, vous déverserez le volume de ce ticket parmi vos volumes disponibles de Carburant d'Aviation Durable, afin de pouvoir l'affecter à un autre client. Ce ticket restera visible dans votre historique."
              )}
            </p>
          </section>
        </main>

        <footer>
          <Button
            icon={Send}
            label={t("Accepter et créditer")}
            variant="primary"
            action={creditTicketSource}
          />

          <Button icon={Return} label={t("Retour")} action={onClose} />
        </footer>
      </Dialog>
    </Portal>
  )
}

export default CreditTicketSource
