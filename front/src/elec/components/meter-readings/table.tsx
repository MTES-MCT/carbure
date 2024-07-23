import Button from "common/components/button"
import { Download } from "common/components/icons"
import Table, { Cell, actionColumn } from "common/components/table"
import { formatDate, formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/application-status"
import { ElecMeterReadingsApplication } from "elec/types"
import { useTranslation } from "react-i18next"
import { compact } from "common/utils/collection"

import { To } from "react-router-dom"

interface MeterReadingsApplicationsTableProps {
	applications: ElecMeterReadingsApplication[]
	onDownloadMeterReadingsApplication: (
		application: ElecMeterReadingsApplication
	) => void
	rowLink?: (row: ElecMeterReadingsApplication) => To
	loading?: boolean
	displayCpo?: boolean
}

const MeterReadingsApplicationsTable: React.FC<
	MeterReadingsApplicationsTableProps
> = ({
	applications,
	onDownloadMeterReadingsApplication,
	rowLink,
	loading,
	displayCpo = false,
}) => {
	const { t } = useTranslation()

	return (
		<Table
			loading={loading}
			rows={applications}
			rowLink={rowLink}
			columns={compact([
				{
					header: t("Statut"),
					cell: (application) => (
						<ApplicationStatus status={application.status} />
					),
				},
				{
					header: t("Période"),
					cell: (application) => (
						<Cell
							text={t("T{{quarter}} {{year}}", {
								quarter: application.quarter,
								year: application.year,
							})}
						/>
					),
				},
				displayCpo && {
					header: t("Aménageur"),
					cell: (application) => <Cell text={`${application.cpo.name}`} />,
				},
				{
					header: t("Points de recharge"),
					cell: (application) => (
						<Cell text={`${formatNumber(application.charge_point_count)}`} />
					),
				},
				{
					header: t("kwh renouvelables"),
					cell: (application) => (
						<Cell
							text={
								`${formatNumber(Math.round(application.energy_total))}` + " kWh"
							}
						/>
					),
				},
				actionColumn<ElecMeterReadingsApplication>((application) =>
					compact([
						<Button
							captive
							variant="icon"
							icon={Download}
							title={t("Exporter les relevés trimestriels")}
							action={() => onDownloadMeterReadingsApplication(application)}
						/>,
					])
				),
			])}
		/>
	)
}

export default MeterReadingsApplicationsTable
