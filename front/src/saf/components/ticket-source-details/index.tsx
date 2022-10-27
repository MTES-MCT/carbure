import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Collapse from "common/components/collapse"
import Dialog from "common/components/dialog"
import HashRoute, { useHashMatch } from "common/components/hash-route"
import { Return, Send, Split } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { formatDate, formatNumber } from "common/utils/formatters"
import { useEffect, useRef } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { LotPreview, SafTicketPreview, SafTicketSource } from "saf/types"
import LotDetails from "transaction-details/components/lots"
import NavigationButtons from "transaction-details/components/lots/navigation"
import { Lot } from "transactions/types"
import * as api from "../../api"
import TicketSourceTag from "../ticket-sources/tag"
import TicketTag from "../tickets/tag"
import TicketAssignment from "./assignment"
import TicketSourceFields from "./fields"

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
  const notify = useNotify()
  const entity = useEntity()
  const match = useHashMatch("ticket-source/:id")
  const portal = usePortal()

  const ticketSourceResponse = useQuery(api.getSafTicketSourceDetails, {
    key: "ticket-source-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })

  const ticketSource = ticketSourceResponse.result?.data?.data
  console.log("ticketSource:", ticketSource)
  // const ticketSource = safTicketSourceDetails //TO TEST
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

  const handleTicketAssigned = (volume: number, clientName: string) => {
    notify(
      t("{{volume}} litres ont bien été assignés à {{clientName}}.", {
        volume,
        clientName,
      }),
      { variant: "success" }
    )
  }

  const showAssignement = () => {
    portal((close) => (
      <TicketAssignment
        ticketSource={ticketSource!}
        onClose={close}
        onTicketAssigned={handleTicketAssigned}
      />
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
            disabled={!ticketSource}
            action={showAssignement}
          />
          <NavigationButtons neighbors={neighbors} closeAction={closeDialog} />
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
                  {ticket.client} - {formatNumber(ticket.volume)} L -{" "}
                  {t("Affecté le")} {formatDate(ticket.created_at)}{" "}
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
  const location = useLocation()
  const navigate = useNavigate()

  const showLotDetails = () => {
    navigate({
      pathname: location.pathname,
      search: location.search,
      hash: `lot/${parent_lot?.id}`,
    })
  }

  return (
    <Collapse isOpen={true} variant="info" icon={Split} label={"Lot Initial"}>
      <section>
        <ul>
          <li>
            {parent_lot ? (
              <Button variant="link" action={showLotDetails}>
                {parent_lot.carbure_id}
              </Button>
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
