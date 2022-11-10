import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Cross, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { useRef } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketStatus } from "saf/types"
import { safTicketDetails } from "saf/__test__/data"
import NavigationButtons from "transaction-details/components/lots/navigation"
import * as api from "../../api"
import TicketTag from "../tickets/tag"
import CancelAssignment from "./cancel-assignment"
import ClientComment from "./client-comment"
import { TicketFields } from "./fields"

export interface TicketDetailsProps {
  neighbors: number[]
}
export const OperatorTicketDetails = ({ neighbors }: TicketDetailsProps) => {
  const { t } = useTranslation()
  const commentRef = useRef<HTMLElement>(null)

  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const match = useHashMatch("ticket/:id")
  const portal = usePortal()

  const ticketResponse = useQuery(api.getOperatorTicketDetails, {
    key: "ticket-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })

  const ticket = ticketResponse.result?.data?.data
  // const ticket = safTicketDetails //TO TEST

  const showCancelModal = () => {
    portal((close) => (
      <CancelAssignment
        ticket={ticket!}
        onClose={() => {
          close()
          closeDialog()
        }}
      />
    ))
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
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
          {[SafTicketStatus.Pending, SafTicketStatus.Rejected].includes(
            ticket?.status!
          ) && (
            <Button
              icon={Cross}
              label={t("Annuler l'affectation")}
              variant="danger"
              disabled={!ticket}
              action={showCancelModal}
            />
          )}

          <NavigationButtons neighbors={neighbors} closeAction={closeDialog} />
        </footer>

        {ticketResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default OperatorTicketDetails