import Table, { Cell } from "common/components/table"
import { formatDate, formatNumber } from "common/utils/formatters"
import { getApplicationAuditLimitDate } from "elec-auditor/helpers"
import { ElecAuditorApplication } from "elec-auditor/types"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"
import ApplicationStatus from "./application-status"

interface ApplicationsTableProps {
  applications: ElecAuditorApplication[]
  rowLink?: (row: ElecAuditorApplication) => To
  loading?: boolean
}

const ApplicationsTable: React.FC<ApplicationsTableProps> = ({
  applications,
  rowLink,
  loading,
}) => {
  const { t } = useTranslation()

  return (
    <Table
      loading={loading}
      rows={applications}
      rowLink={rowLink}
      columns={[
        {
          header: t("Statut"),
          cell: (application) => (
            <ApplicationStatus status={application.status} />
          ),
        },
        {
          header: t("Ordre de côntrole"),
          cell: (application) => (
            <Cell text={`${formatDate(application.audit_order_date!)}`} />
          ),
        },
        {
          header: t("Aménageur"),
          cell: (application) => <Cell text={`${application.cpo.name}`} />,
        },
        {
          header: t("Stations"),
          cell: (application) => (
            <Cell text={`${formatNumber(application.station_count)}`} />
          ),
        },
        {
          header: t("Points de recharge"),
          cell: (application) => (
            <Cell text={`${formatNumber(application.charge_point_count)}`} />
          ),
        },
        {
          header: t("Date limite"),
          cell: (application) => {
            let limitDate = getApplicationAuditLimitDate(
              application.audit_order_date!
            )
            return <Cell text={`${formatDate(limitDate)}`} />
          },
        },
      ]}
    />
  )
}

export default ApplicationsTable
