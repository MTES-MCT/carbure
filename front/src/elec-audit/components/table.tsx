import Button from "common/components/button"
import { Download } from "common/components/icons"
import Table, { Cell, actionColumn } from "common/components/table"
import { compact } from "common/utils/collection"
import { formatDate, formatNumber } from "common/utils/formatters"
import { getApplicationAuditLimitDate } from "elec-audit/helpers"
import { ElecAuditApplication } from "elec-audit/types"
import { ElecChargePointsApplication } from "elec/types"
import { useTranslation } from "react-i18next"
import { To } from "react-router-dom"
import ApplicationStatus from "./application-status"

interface ElecAuditApplicationsTableProps {
  applications: ElecAuditApplication[];
  rowLink?: (row: ElecAuditApplication) => To
  loading?: boolean;
}

const ElecAuditApplicationsTable: React.FC<ElecAuditApplicationsTableProps> = ({
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
          cell: (application) => <ApplicationStatus status={application.status} />,
        },
        {
          header: t("Ordre de côntrole"),
          cell: (application) => (
            <Cell
              text={`${formatDate(application.audit_order_date!)}`}
            />
          ),
        },
        {
          header: t("Aménageur"),
          cell: (application) => (
            <Cell
              text={`${application.cpo.name}`}
            />
          ),
        },
        {
          header: t("Stations"),
          cell: (application) => (
            <Cell
              text={`${formatNumber(application.station_count)}`}
            />
          ),
        },
        {
          header: t("Points de recharge"),
          cell: (application) => (
            <Cell
              text={`${formatNumber(application.charge_point_count)}`}
            />
          ),
        },
        {
          header: t("Date limité"),
          cell: (application) => {
            let limitDate = getApplicationAuditLimitDate(application.audit_order_date!)
            return <Cell
              text={`${formatDate(limitDate)}`}
            />
          },
        },
      ]}
    />
  );
};

export default ElecAuditApplicationsTable;