import { useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import { Snapshot, AdminStatus } from "../types"
import Tabs from "common/components/tabs"
import { Loader } from "common/components/icons"
import { formatNumber } from "common/utils/formatters"

export interface StatusTabsProps {
	loading: boolean
	count: Snapshot["lots"] | undefined
}

export const StatusTabs = ({
	loading,
	count = defaultCount,
}: StatusTabsProps) => {
	const { t } = useTranslation()

	return (
		<Tabs
			variant="main"
			tabs={[
				{
					key: "alerts",
					path: "alerts",
					label: (
						<StatusRecap
							loading={loading}
							count={count.alerts}
							label={t("Signalements", { count: count.alerts })}
						/>
					),
				},
				{
					key: "lots",
					path: "lots",
					label: (
						<StatusRecap
							loading={loading}
							count={count.lots}
							label={t("Lots", { count: count.lots })}
						/>
					),
				},
				{
					key: "stocks",
					path: "stocks",
					label: (
						<StatusRecap
							loading={loading}
							count={count.stocks}
							label={t("Stocks", { count: count.stocks })}
						/>
					),
				},
			]}
		/>
	)
}

const defaultCount: Snapshot["lots"] = {
	alerts: 0,
	lots: 0,
	stocks: 0,
	pinned: 0,
}

interface StatusRecapProps {
	loading: boolean
	count: number
	label: string
	tofix?: number
}

const StatusRecap = ({ loading, count = 0, label }: StatusRecapProps) => {
	return (
		<>
			<p style={{ fontWeight: "normal" }}>
				{loading ? <Loader size={20} /> : formatNumber(count)}{" "}
			</p>
			<strong>{label}</strong>
		</>
	)
}

export function useStatus() {
	const match = useMatch("/org/:entity/controls/:year/:status/*") // prettier-ignore
	return (match?.params.status ?? "unknown") as AdminStatus
}

export default StatusTabs
