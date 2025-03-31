import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketStatus } from "saf/types"
import TicketTag from "../../components/tickets/tag"
import ClientComment from "../../components/ticket-details/client-comment"
import { TicketFields } from "../../components/ticket-details/fields"
import RejectAssignment from "../../components/ticket-details/reject-assignment"
import {
  NavigationButtons,
  NavigationButtonsProps,
} from "common/components/navigation"
import AcceptAssignment from "./accept-assignment"
import { useSafRules } from "saf/hooks/useSafRules"
import { getTicketDetails } from "saf/api"

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
  const entity = useEntity()
  const match = useHashMatch("ticket/:id")
  const portal = usePortal()
  const { canUpdateTicket } = useSafRules()

  const ticketResponse = useQuery(getTicketDetails, {
    key: "ticket-details",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const ticket = ticketResponse.result?.data

  const showAcceptModal = () => {
    portal((close) => <AcceptAssignment ticket={ticket!} onClose={close} />)
  }

  const showRejectModal = () => {
    portal((close) => <RejectAssignment ticket={ticket!} onClose={close} />)
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={
          <Dialog.Title>
            <TicketTag status={ticket?.status} />
            {t("Ticket n°")}
            {ticket?.carbure_id ?? "..."}
          </Dialog.Title>
        }
        footer={
          <>
            {baseIdsList && baseIdsList.length > 0 && (
              <NavigationButtons
                limit={limit}
                total={total}
                fetchIdsForPage={fetchIdsForPage}
                baseIdsList={baseIdsList}
              />
            )}
            {ticket?.status === SafTicketStatus.PENDING && canUpdateTicket && (
              <>
                <Button
                  iconId="ri-check-line"
                  customPriority="success"
                  disabled={!ticket}
                  onClick={showAcceptModal}
                >
                  {t("Accepter")}
                </Button>
                <Button
                  iconId="ri-close-line"
                  customPriority="danger"
                  disabled={!ticket}
                  onClick={showRejectModal}
                >
                  {t("Refuser")}
                </Button>
              </>
            )}
          </>
        }
      >
        <section>
          <TicketFields ticket={ticket} />
        </section>
        <ClientComment ticket={ticket} />

        {ticketResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default ClientTicketDetails
