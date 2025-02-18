import Button from "common/components/button"
import { formatDate, formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketPreview } from "saf/types"
import TicketTag from "../../../components/tickets/tag"
import { SafTicketSource } from "../types"
import { Collapse } from "common/components/collapse2"

const AssignedTickets = ({
  ticketSource,
}: {
  ticketSource: SafTicketSource | undefined
}) => {
  const { t } = useTranslation()
  const location = useLocation()

  const navigate = useNavigate()

  const showTicket = (ticket: SafTicketPreview) => {
    navigate({
      pathname: location.pathname,
      search: location.search,
      hash: `ticket/${ticket?.id}`,
    })
  }

  if (!ticketSource) return null

  return (
    <Collapse
      defaultExpanded
      label={
        t("Tickets affectés") +
        ` (${formatNumber(ticketSource.assigned_volume)}L/${formatNumber(
          ticketSource.total_volume
        )})`
      }
    >
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
    </Collapse>
  )
}

export default AssignedTickets
