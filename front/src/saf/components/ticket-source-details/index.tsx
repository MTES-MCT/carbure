import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Fieldset } from "common/components/form"
import { useHashMatch } from "common/components/hash-route"
import { Return, Send, Split } from "common/components/icons"
import { TextInput } from "common/components/input"
import Portal from "common/components/portal"
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
import { LotPreview, SafTicketPreview } from "saf/types"
import { useEffect, useRef } from "react"
import NavigationButtons from "transaction-details/components/lots/navigation"
import TicketTag from "../tickets/tag"

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
  const match = useHashMatch("lot/:id")

  const ticketSourceResponse = useQuery(api.getSafTicketSourceDetails, {
    key: "ticket-source-details",
    params: [entity.id, parseInt(match?.params.id!)],
  })
  // const ticketSource = ticketSourceResponse.result?.data.data
  const ticketSource = safTicketSourceDetails //TO TEST
  const hasAssignements = ticketSource?.assigned_tickets?.length > 0

  useEffect(() => {
    if (hasAssignements && assignementsRef?.current)
      assignementsRef.current.scrollIntoView({
        block: "end",
        behavior: "smooth",
      })
  }, [assignementsRef, hasAssignements])

  const closeDialog = () => {
    invalidate("ticket-sources")
    navigate({ search: location.search, hash: "#" })
  }

  const showAssignement = () => {}

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          <TicketSourceTag ticketSource={ticketSource} />
          <h1>
            {t("Volume SAF n°")} {ticketSource?.carbure_id}
          </h1>
        </header>

        <main>
          <section>
            <TicketSourceFields ticketSource={ticketSource} />
          </section>
          {hasAssignements && (
            <section>
              <AssignedTickets tickets={ticketSource.assigned_tickets} />
            </section>
          )}
          <section>
            <LotOrigin parent_lot={ticketSource.parent_lot} />
          </section>

          <section ref={assignementsRef}></section>
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

const AssignedTickets = ({ tickets }: { tickets: SafTicketPreview[] }) => {
  const { t } = useTranslation()

  const showTicket = (ticket: SafTicketPreview) => {}

  return (
    <Collapse
      isOpen={true}
      variant="info"
      icon={Split}
      label={"Tickets affectés"}
    >
      <section>
        <ul>
          {tickets.map((ticket) => {
            return (
              <li>
                <Button variant="link" action={() => showTicket(ticket)}>
                  {ticket.client_name} - {formatNumber(ticket.volume)}L -{" "}
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
