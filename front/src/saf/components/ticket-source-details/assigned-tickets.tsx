import Button from "common/components/button"
import Collapse from "common/components/collapse"
import { Send } from "common/components/icons"
import { formatDate, formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import { SafTicketPreview, SafTicketSource } from "saf/types"
import TicketTag from "../tickets/tag"

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

export default AssignedTickets
