import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Check, Cross } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketStatus } from "saf/types"
import NavigationButtons from "transaction-details/components/lots/navigation"
import * as api from "../../api"
import TicketTag from "../tickets/tag"
import ClientComment from "./client-comment"
import { TicketFields } from "./fields"
import RejectAssignment from "./reject-assignment"

export interface TicketDetailsProps {
  neighbors: number[]
}
export const ClientTicketDetails = ({ neighbors }: TicketDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotify()
  const entity = useEntity()
  const match = useHashMatch("ticket/:id")
  const portal = usePortal()

  const ticketResponse = useQuery(api.getAirlineTicketDetails, {
    key: "ticket-details",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const acceptSafTicket = useMutation(api.acceptSafTicket, {
    invalidates: ["ticket-details", "tickets", "airline-snapshot"],
    onSuccess: () => {
      closeDialog()
      notify(t("Le ticket a été accepté."), { variant: "success" })
    },
  })

  const ticket = ticketResponse.result?.data?.data
  // const ticket = safTicketDetails //TO TEST

  const showRejectModal = () => {
    portal((close) => <RejectAssignment ticket={ticket!} onClose={close} />)
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const acceptTicket = async () => {
    await acceptSafTicket.execute(entity.id, ticket!.id)
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <TicketTag big status={ticket?.status} />
          <h1>
            {t("Ticket n°")}
            {ticket?.carbure_id ?? "..."}
          </h1>
        </header>

        <main>
          <section>
            <TicketFields ticket={ticket} />
          </section>
          <ClientComment ticket={ticket} />
        </main>

        <footer>
          {ticket?.status === SafTicketStatus.Pending && (
            <>
              <Button
                icon={Check}
                label={t("Accepter")}
                variant="success"
                disabled={!ticket}
                action={acceptTicket}
              />
              <Button
                icon={Cross}
                label={t("Refuser")}
                variant="danger"
                disabled={!ticket}
                action={showRejectModal}
              />
            </>
          )}
          <NavigationButtons neighbors={neighbors} closeAction={closeDialog} />
        </footer>

        {ticketResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default ClientTicketDetails
