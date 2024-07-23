import Alert from "common/components/alert"
import Button from "common/components/button"
import { Filter } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SafTicketSource } from "saf/types"
import TicketsGroupedAssignment from "../assignment/grouped-assignment"

export interface TicketSourcesSummaryProps {
	ticketSources: SafTicketSource[]
}

export const TicketSourcesSummary = ({
	ticketSources,
}: TicketSourcesSummaryProps) => {
	const { t } = useTranslation()
	const portal = usePortal()

	const notify = useNotify()
	const totalVolume = ticketSources.reduce(
		(total, ticketSource) => total + ticketSource.total_volume,
		0
	)
	const assignedVolume = ticketSources.reduce(
		(total, ticketSource) => total + ticketSource.assigned_volume,
		0
	)
	const remainingVolume = totalVolume - assignedVolume

	const handleTicketsAssigned = (
		volume: number,
		clientName: string,
		assignedTicketsCount: number
	) => {
		notify(
			t(
				"{{volume}} litres ont bien été affectés à {{clientName}}. {{assignedTicketsCount}} tickets ont été générés.",
				{
					volume,
					clientName,
					assignedTicketsCount,
				}
			),
			{ variant: "success" }
		)
	}

	const showGroupedAssignement = () => {
		portal((close) => (
			<TicketsGroupedAssignment
				ticketSources={ticketSources}
				remainingVolume={remainingVolume}
				onClose={close}
				onTicketsAssigned={handleTicketsAssigned}
			/>
		))
	}

	return (
		<Alert icon={Filter} variant="info">
			<p>
				{t(
					"{{volumeCount}} volumes sélectionnés pour un total de {{remainingVolume}} L",
					{
						volumeCount: ticketSources.length,
						remainingVolume: formatNumber(remainingVolume),
					}
				)}
			</p>

			<Button
				asideX
				variant="primary"
				label={t("Affecter les {{volumeCount}} volumes", {
					volumeCount: ticketSources.length,
				})}
				action={showGroupedAssignement}
			/>
		</Alert>
	)
}
