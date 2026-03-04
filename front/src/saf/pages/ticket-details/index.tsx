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
import TicketTag from "saf/components/ticket-tag"
import CancelAssignment from "./components/cancel-assignment"
import ClientComment from "saf/pages/ticket-details/components/client-comment"
import CreditTicketSource from "./components/credit-ticket-source"
import { TicketFields } from "saf/pages/ticket-details/components/fields"
import LinkedTicketSource from "./components/linked-ticket-source"
import RejectAssignment from "saf/pages/ticket-details/components/reject-assignment"
import {
  NavigationButtons,
  NavigationButtonsProps,
} from "common/components/navigation"
import { UserRole } from "common/types"
import { getTicketDetails } from "saf/api"
import AcceptAssignment from "./components/accept-assignment"
import SafOrigin from "saf/components/saf_origin"

export type TicketDetailsProps = Partial<
  Omit<NavigationButtonsProps, "closeAction">
>
export const TicketDetails = ({
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

  const ticketResponse = useQuery(getTicketDetails, {
    key: "ticket-details",
    params: [entity.id, parseInt(match?.params.id ?? "")],
  })

  const ticket = ticketResponse.result?.data

  const canWrite = entity.hasRights(UserRole.ReadWrite, UserRole.Admin)

  const isClient = ticket?.client === entity.name
  const isSupplier = ticket?.supplier === entity.name
  const isAdmin = entity.isAdmin || entity.isExternal

  const isPending = ticket?.status === SafTicketStatus.PENDING
  const isCancelable = isPending || ticket?.status === SafTicketStatus.REJECTED

  const hasChildVolume = Boolean(ticket?.child_ticket_sources.length)

  const showCancelModal = () => {
    portal((close) => (
      <CancelAssignment
        ticket={ticket!}
        onCancel={closeDialog}
        onClose={close}
      />
    ))
  }

  const showAcceptModal = () => {
    portal((close) => {
      if (entity.isAirline) {
        return (
          <AcceptAssignment //
            ticket={ticket!}
            onClose={close}
          />
        )
      } else {
        return (
          <CreditTicketSource
            ticket={ticket!}
            onClose={close}
            onCredit={closeDialog}
          />
        )
      }
    })
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
            {ticket?.carbure_id ?? "..."} - {ticket?.supplier}
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

            {isClient && isPending && (
              <>
                <Button
                  iconId="ri-check-line"
                  customPriority="success"
                  onClick={showAcceptModal}
                  disabled={!canWrite}
                >
                  {t("Accepter")}
                </Button>
                <Button
                  iconId="ri-close-line"
                  customPriority="danger"
                  onClick={showRejectModal}
                  disabled={!canWrite}
                >
                  {t("Refuser")}
                </Button>
              </>
            )}

            {isSupplier && isCancelable && (
              <Button
                iconId="ri-close-line"
                customPriority="danger"
                onClick={showCancelModal}
                disabled={!canWrite}
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

        <SafOrigin ticket={ticket} canAccess={isSupplier || isAdmin} />

        {hasChildVolume && (isClient || isAdmin) && (
          <LinkedTicketSource
            ticket_source={ticket?.child_ticket_sources[0]}
            title={t("Volume enfant")}
          />
        )}

        {ticketResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default TicketDetails
