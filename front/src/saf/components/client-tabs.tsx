import { Loader } from "common/components/icons"
import { Col, Row } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { compact } from "common/utils/collection"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import css from "./tabs.module.css"

import { SafClientSnapshot, SafTicketStatus } from "saf/types"

export interface StatusTabsProps {
	loading: boolean
	count?: SafClientSnapshot
}

export const ClientTabs = ({
	loading,
	count = defaultCount,
}: StatusTabsProps) => {
	const { t } = useTranslation()

	return (
		<Tabs
			variant="main"
			className={css.safTabs}
			tabs={compact([
				{
					key: SafTicketStatus.Pending,
					path: `tickets/${SafTicketStatus.Pending.toLowerCase()}`,
					label: (
						<Row>
							<Col>
								<p>
									{loading ? (
										<Loader size={20} />
									) : (
										formatNumber(count.tickets_pending)
									)}
								</p>
								<strong>
									{t("Tickets en attente", {
										count: count.tickets_pending,
									})}
								</strong>
							</Col>
						</Row>
					),
				},
				{
					key: SafTicketStatus.Accepted,
					path: `tickets/${SafTicketStatus.Accepted.toLowerCase()}`,
					label: (
						<Row>
							<Col>
								<p>
									{loading ? (
										<Loader size={20} />
									) : (
										formatNumber(count.tickets_accepted)
									)}
								</p>
								<strong>
									{t("Tickets acceptés", { count: count.tickets_accepted })}
								</strong>
							</Col>
						</Row>
					),
				},
			])}
		/>
	)
}

const defaultCount: SafClientSnapshot = {
	tickets_pending: 0,
	tickets_accepted: 0,
}

export function useAutoStatus() {
	const matchStatus = useMatch("/org/:entity/saf/:year/tickets/:status/*")
	const status = matchStatus?.params.status as SafTicketStatus
	return (status.toUpperCase() as SafTicketStatus) ?? SafTicketStatus.Pending
}

export default ClientTabs
