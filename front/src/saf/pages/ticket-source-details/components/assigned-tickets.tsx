import { Button } from "common/components/button2"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import TicketTag from "saf/components/ticket-tag"
import { SafTicketSource } from "saf/types"
import { Collapse } from "common/components/collapse2"
import { Ellipsis } from "common/components/scaffold"

const AssignedTickets = ({
  ticketSource,
}: {
  ticketSource: SafTicketSource | undefined
}) => {
  const { t } = useTranslation()

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
              <Button
                customPriority="link"
                linkProps={{ href: `#ticket/${ticket?.id}` }}
              >
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
