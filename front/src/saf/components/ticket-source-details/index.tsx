import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Fieldset } from "common/components/form"
import HashRoute, { useHashMatch } from "common/components/hash-route"
import { Return, Send, Split } from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { invalidate } from "common/hooks/invalidate"
import { formatDate, formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { safTicketSourceDetails } from "saf/__test__/data"
import * as api from "../../api"
import TicketSourceTag from "../ticket-sources/tag"
import TicketSourceFields from "./fields"
import Collapse from "common/components/collapse"
import { LotPreview, SafTicketPreview, SafTicketSource } from "saf/types"
import { useEffect, useRef } from "react"
import NavigationButtons from "transaction-details/components/lots/navigation"
import TicketTag from "../tickets/tag"
import { cp } from "fs/promises"
import TicketAssignment from "./assignment"

export interface TicketSourceDetailsProps {
  neighbors: number[]
}
export const TicketSourceDetails = ({
  neighbors,
}: TicketSourceDetailsProps) => {
  const { t } = useTranslation()
  const assignementsRef = useRef<HTMLElement>(null)

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const match = useHashMatch("ticket-source/:id")
  const portal = usePortal()

  const ticketSourceResponse = useQuery(api.getSafTicketSourceDetails, {
    key: "ticket-source-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })

  // const ticketSource = ticketSourceResponse.result?.data?.data
  const ticketSource = safTicketSourceDetails //TO TEST
  const hasAssignements = ticketSource
    ? ticketSource?.assigned_tickets?.length > 0
    : false

  useEffect(() => {
    if (hasAssignements && assignementsRef?.current)
      assignementsRef.current.scrollIntoView({
        block: "end",
        behavior: "smooth",
      })
  }, [assignementsRef, hasAssignements])

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const showAssignement = () => {
    portal((close) => (
      <TicketAssignment ticketSource={ticketSource} onClose={close} />
    ))
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <TicketSourceTag ticketSource={ticketSource} />
          <h1>
            {t("Volume CAD n°")}
            {ticketSource?.carbure_id ?? "..."}
          </h1>
        </header>

        <main>
          <section>
            <TicketSourceFields ticketSource={ticketSource} />
          </section>
          {hasAssignements && (
            <section ref={assignementsRef}>
              <AssignedTickets ticketSource={ticketSource} />
            </section>
          )}
          <section>
            <LotOrigin parent_lot={ticketSource?.parent_lot} />
          </section>
        </main>

        <footer>
          <Button
            icon={Send}
            label={t("Affecter")}
            variant="primary"
            action={showAssignement}
          />
          <NavigationButtons neighbors={neighbors} />

          <Button icon={Return} label={t("Retour")} action={closeDialog} />
        </footer>

        {ticketSourceResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default TicketSourceDetails

const AssignedTickets = ({
  ticketSource,
}: {
  ticketSource: SafTicketSource | undefined
}) => {
  const { t } = useTranslation()

  const showTicket = (ticket: SafTicketPreview) => {
    //TODO open ticket modal
  }

  if (!ticketSource) return null

  return (
    <Collapse
      isOpen={true}
      variant="info"
      icon={Send}
      label={
        t("Tickets affectés") +
        ` (${formatNumber(ticketSource.assigned_volume)}L/${formatNumber(
          ticketSource.total_volume
        )})`
      }
    >
      <section>
        <ul>
          {ticketSource.assigned_tickets.map((ticket) => {
            return (
              <li key={ticket.id}>
                <Button variant="link" action={() => showTicket(ticket)}>
                  {ticket.client_name} - {formatNumber(ticket.volume)} L -{" "}
                  {t("Affecté le")} {formatDate(ticket.date)}{" "}
                </Button>{" "}
                <TicketTag status={ticket.status} small />
              </li>
            )
          })}
        </ul>
      </section>
      <footer></footer>
    </Collapse>
  )
}

const LotOrigin = ({ parent_lot }: { parent_lot?: LotPreview }) => {
  const { t } = useTranslation()
  return (
    <Collapse isOpen={true} variant="info" icon={Split} label={"Lot Initial"}>
      <section>
        <ul>
          <li>
            {parent_lot ? (
              <Button variant="link">{parent_lot.carbure_id}</Button>
            ) : (
              t("Inconnu")
            )}
          </li>
        </ul>
      </section>
      <footer></footer>
    </Collapse>
  )
}
