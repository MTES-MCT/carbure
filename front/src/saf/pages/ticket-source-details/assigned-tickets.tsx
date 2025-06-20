import { Button } from "common/components/button2"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafAssignedTicket } from "saf/types"
import TicketTag from "saf/components/tickets/tag"
import { SafTicketSource } from "saf/types"
import { Collapse } from "common/components/collapse2"
import { Ellipsis } from "common/components/scaffold"

const AssignedTickets = ({
  ticketSource,
}: {
  ticketSource: SafTicketSource | undefined
}) => {
  const { t } = useTranslation()
  const location = useLocation()

  const navigate = useNavigate()

  const showTicket = (ticket: SafAssignedTicket) => {
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
              <Button customPriority="link" onClick={() => showTicket(ticket)}>
                <Ellipsis>{ticket.client}</Ellipsis> -{" "}
                {formatNumber(ticket.volume)} L -{" "}
                {formatDate(
                  `${formatPeriod(ticket.assignment_period)}-01`,
                  "MM/yyyy"
                )}{" "}
                {`(${t("créé le")} ${formatDate(ticket.created_at)})`}{" "}
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
