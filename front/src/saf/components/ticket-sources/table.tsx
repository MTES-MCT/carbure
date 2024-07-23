import Button from "common/components/button"
import Table, { Cell, Order, selectionColumn } from "common/components/table"
import { compact } from "common/utils/collection"
import { formatNumber, formatPeriod } from "common/utils/formatters"
import { memo } from "react"
import { useTranslation } from "react-i18next"
import { To, useLocation, useNavigate } from "react-router-dom"
import { SafTicketSource, SafTicketSourceStatus } from "saf/types"
import { TicketSourceTag } from "./tag"

export interface TicketSourcesTableProps {
	loading: boolean
	ticketSources: SafTicketSource[]
	order: Order | undefined
	rowLink: (ticketSource: SafTicketSource) => To
	onOrder: (order: Order | undefined) => void
	selected: number[]
	onSelect: (selected: number[]) => void
	status: SafTicketSourceStatus
}

export const TicketSourcesTable = memo(
	({
		loading,
		ticketSources,
		order,
		rowLink,
		onOrder,
		selected,
		onSelect,
		status,
	}: TicketSourcesTableProps) => {
		const columns = useColumns()
		return (
			<Table
				loading={loading}
				order={order}
				onOrder={onOrder}
				rowLink={rowLink}
				rows={ticketSources}
				columns={compact([
					status === SafTicketSourceStatus.Available &&
						selectionColumn(
							ticketSources,
							selected,
							onSelect,
							(ticketSource) => ticketSource.id
						),
					columns.status,
					columns.availableVolume,
					columns.clients,
					columns.period,
					columns.feedstock,
					columns.ghgReduction,
					columns.parentLot,
				])}
			/>
		)
	}
)

export function useColumns() {
	const { t } = useTranslation()
	return {
		status: {
			header: t("Statut"),
			cell: (ticketSource: SafTicketSource) => (
				<TicketSourceTag ticketSource={ticketSource} />
			),
		},

		availableVolume: {
			key: "volume",
			header: t("Volumes disponibles"),
			cell: (ticketSource: SafTicketSource) => (
				<Cell
					text={`${formatNumber(
						ticketSource.total_volume - ticketSource.assigned_volume
					)} L`}
					sub={`/${formatNumber(ticketSource.total_volume)} L`}
				/>
			),
		},

		clients: {
			// key: "clients",
			header: t("Clients"),
			cell: (ticketSource: SafTicketSource) => {
				const value =
					ticketSource.assigned_tickets.length > 0
						? ticketSource.assigned_tickets.map((t) => t.client).join(", ")
						: "-"
				return <Cell text={value} />
			},
		},

		period: {
			key: "delivery",
			header: t("Livraison"),
			cell: (ticketSource: SafTicketSource) => {
				return (
					<Cell
						text={
							ticketSource.delivery_period
								? formatPeriod(ticketSource.delivery_period)
								: t("N/A")
						}
					/>
				)
			},
		},

		feedstock: {
			key: "feedstock",
			header: t("Matière première"),
			cell: (ticketSource: SafTicketSource) => (
				<Cell
					text={t(ticketSource.feedstock?.code ?? "", { ns: "feedstocks" })}
					sub={t(ticketSource.country_of_origin?.code_pays ?? "", {
						ns: "countries",
					})}
				/>
			),
		},

		ghgReduction: {
			small: true,
			key: "ghg_reduction",
			header: t("Réd. GES"),
			cell: (ticketSource: SafTicketSource) => {
				return <Cell text={`${ticketSource.ghg_reduction.toFixed(0)}%`} />
			},
		},

		parentLot: {
			key: "parent_lot",
			header: t("Lot parent"),
			cell: (ticketSource: SafTicketSource) => (
				<ParentLotButton lot={ticketSource.parent_lot} />
			),
		},
	}
}

export default TicketSourcesTable

export interface ParentLotButtonProps {
	lot?: {
		id: number
		carbure_id: string
	}
}

export const ParentLotButton = ({ lot }: ParentLotButtonProps) => {
	const { t } = useTranslation()
	const navigate = useNavigate()
	const location = useLocation()

	if (!lot) return <Cell text={t("N/A")} />

	const showLotDetails = () => {
		navigate({
			pathname: location.pathname,
			search: location.search,
			hash: `lot/${lot!.id}`,
		})
	}

	return (
		<Button
			captive
			variant="link"
			title={t("Lot initial")}
			label={`#${lot.carbure_id}`}
			action={showLotDetails}
		/>
	)
}
