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
import * as api from "../api"
import TicketTag from "../../../components/tickets/tag"
import CancelAssignment from "./cancel-assignment"
import ClientComment from "../../../components/ticket-details/client-comment"
import CreditTicketSource from "./credit-ticket-source"
import { TicketFields } from "../../../components/ticket-details/fields"
import LinkedTicketSource from "./linked-ticket-source"
import RejectAssignment from "../../../components/ticket-details/reject-assignment"
import {
  NavigationButtons,
  NavigationButtonsProps,
} from "common/components/navigation"
import { UserRole } from "common/types"

export type TicketDetailsProps = Partial<
  Omit<NavigationButtonsProps, "closeAction">
>
export const OperatorTicketDetails = ({
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

  const ticketResponse = useQuery(api.getOperatorTicketDetails, {
    key: "ticket-details",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const ticket = ticketResponse.result?.data
  const canUpdateTicket =
    entity.hasRights(UserRole.ReadWrite) || entity.hasRights(UserRole.Admin)

  const showCancelModal = () => {
    portal((close) => (
      <CancelAssignment
        ticket={ticket!}
        onCancel={closeDialog}
        onClose={close}
      />
    ))
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const showRejectModal = () => {
    portal((close) => <RejectAssignment ticket={ticket!} onClose={close} />)
  }

  const showAcceptModal = async () => {
    portal((close) => (
      <CreditTicketSource
        ticket={ticket!}
        onClose={() => {
          close()
          closeDialog()
        }}
      />
    ))
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
            {baseIdsList && baseIdsList.length > 0 && fetchIdsForPage && (
              <NavigationButtons
                limit={limit}
                total={total ?? 0}
                fetchIdsForPage={fetchIdsForPage}
                baseIdsList={baseIdsList}
              />
            )}
            {ticket?.status === SafTicketStatus.PENDING &&
              ticket?.client === entity.name && (
                <>
                  <Button
                    iconId="ri-check-line"
                    customPriority="success"
                    onClick={showAcceptModal}
                    disabled={!canUpdateTicket}
                  >
                    {t("Accepter")}
                  </Button>
                  <Button
                    iconId="ri-close-line"
                    customPriority="danger"
                    onClick={showRejectModal}
                    disabled={!canUpdateTicket}
                  >
                    {t("Refuser")}
                  </Button>
                </>
              )}

            {ticket?.client !== entity.name &&
              ticket?.status &&
              [SafTicketStatus.PENDING, SafTicketStatus.REJECTED].includes(
                ticket?.status
              ) && (
                <Button
                  iconId="ri-close-line"
                  customPriority="danger"
                  onClick={showCancelModal}
                  disabled={!canUpdateTicket}
                >
                  {t("Annuler l'affectation")}
                </Button>
              )}
          </>
        }
      >
        <section>
          <TicketFields ticket={ticket} />
        </section>
        <ClientComment ticket={ticket} />

        {ticket?.supplier === entity.name && (
          <LinkedTicketSource
            ticket_source={ticket.parent_ticket_source}
            title={t("Volume parent")}
          />
        )}
        {ticketResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default OperatorTicketDetails
