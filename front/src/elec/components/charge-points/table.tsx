import Button from "common/components/button"
import { Download } from "common/components/icons"
import Table, { Cell, actionColumn } from "common/components/table"
import { formatDate, formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/application-status"
import { ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"
import { compact } from "common/utils/collection"

import { To } from "react-router-dom"

interface ChargePointsApplicationsTableProps {
  applications: ElecChargePointsApplication[]
  onDownloadChargePointsApplication: (
    application: ElecChargePointsApplication
  ) => void
  rowLink?: (row: ElecChargePointsApplication) => To
  loading?: boolean
  displayCpo?: boolean
}

const ChargePointsApplicationsTable: React.FC<
  ChargePointsApplicationsTableProps
> = ({
  applications,
  onDownloadChargePointsApplication,
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
          header: t("Date d'ajout"),
          cell: (application) => (
            <Cell text={`${formatDate(application.application_date)}`} />
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
          header: t("Puissance cumulée"),
          cell: (application) => (
            <Cell
              text={`${formatNumber(Math.round(application.power_total))} kW`}
            />
          ),
        },
        actionColumn<ElecChargePointsApplication>((application) =>
          compact([
            <Button
              captive
              variant="icon"
              icon={Download}
              title={t("Exporter les points de recharge")}
              action={() => onDownloadChargePointsApplication(application)}
            />,
          ])
        ),
      ])}
    />
  )
}

export default ChargePointsApplicationsTable
