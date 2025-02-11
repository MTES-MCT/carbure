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
import * as api from "./api"
import TicketTag from "../../components/tickets/tag"
import ClientComment from "../../components/ticket-details/client-comment"
import { TicketFields } from "../../components/ticket-details/fields"
import RejectAssignment from "../../components/ticket-details/reject-assignment"
import {
  NavigationButtons,
  NavigationButtonsProps,
} from "common/components/navigation"

export type TicketDetailsProps = Omit<NavigationButtonsProps, "closeAction">

export const ClientTicketDetails = ({
  limit,
  total,
  fetchIdsForPage,
  baseIdsList,
}: TicketDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()
  const notify = useNotify()
  const entity = useEntity()
  const match = useHashMatch("ticket/:id")
  const portal = usePortal()

  const ticketResponse = useQuery(api.getAirlineTicketDetails, {
    key: "ticket-details",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const acceptSafTicket = useMutation(api.acceptSafTicket, {
    invalidates: ["tickets", "airline-snapshot"],
    onSuccess: () => {
      closeDialog()
      notify(t("Le ticket a été accepté."), { variant: "success" })
    },
  })

  const ticket = ticketResponse.result?.data

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
          {ticket?.status === SafTicketStatus.PENDING && (
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
          {baseIdsList && baseIdsList.length > 0 && (
            <NavigationButtons
              limit={limit}
              total={total}
              fetchIdsForPage={fetchIdsForPage}
              baseIdsList={baseIdsList}
              closeAction={closeDialog}
            />
          )}
        </footer>

        {ticketResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default ClientTicketDetails
