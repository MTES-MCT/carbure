import Tabs from "common/components/tabs"
import { useTranslation } from "react-i18next"
import { SafOperatorSnapshot, SafTicketSourceStatus } from "saf/types"

interface StatusSwitcherProps {
	status: SafTicketSourceStatus
	count: SafOperatorSnapshot | undefined
	onSwitch: (status: SafTicketSourceStatus) => void
}
export const StatusSwitcher = ({
	status,
	count,
	onSwitch,
}: StatusSwitcherProps) => {
	const { t } = useTranslation()

	return (
		<Tabs
			keepSearch
			variant="switcher"
			focus={status}
			onFocus={(status) => onSwitch(status as SafTicketSourceStatus)}
			tabs={[
				{
					key: SafTicketSourceStatus.Available,
					path: SafTicketSourceStatus.Available.toLowerCase(),
					label: `${t("Disponible")} (${count?.ticket_sources_available ?? 0})`,
				},
				{
					key: SafTicketSourceStatus.History,
					path: SafTicketSourceStatus.History.toLowerCase(),
					label: `${t("Historique")} (${count?.ticket_sources_history ?? 0})`,
				},
			]}
		/>
	)
}
