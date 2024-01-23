import { EntityManager } from "carbure/hooks/entity"
import Button from "common/components/button"
import { Check, Cross, Download } from "common/components/icons"
import { usePortal } from "common/components/portal"
import Table, { Cell, actionColumn } from "common/components/table"
import { formatDate, formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/charge-points/application-status"
import { ElecChargePointsApplication, ElecChargePointsApplicationStatus } from "elec/types"
import { useTranslation } from "react-i18next"
// import { elecChargePointsApplications } from "elec/__test__/data"
import { compact } from "common/utils/collection"

import { To } from "react-router-dom"

interface ChargePointsApplicationsTableProps {
  applications: ElecChargePointsApplication[];
  onDownloadChargePointsApplication: (application: ElecChargePointsApplication) => void;
  rowLink?: (row: ElecChargePointsApplication) => To
  loading?: boolean;
}

const ChargePointsApplicationsTable: React.FC<ChargePointsApplicationsTableProps> = ({
  applications,
  onDownloadChargePointsApplication,
  rowLink,
  loading
}) => {

  const { t } = useTranslation()
  const portal = usePortal()

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
          header: t("Date d'ajout"),
          cell: (application) => (
            <Cell
              text={`${formatDate(application.application_date)}`}
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
          header: t("Puissance cumulée"),
          cell: (application) => (
            <Cell
              text={`${formatNumber(Math.round(application.power_total))}` + " kW"}
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
            // entity.isAdmin && application.status === ElecChargePointsApplicationStatus.Pending && (
            //   <Button
            //     captive
            //     variant="icon"
            //     icon={Check}
            //     title={t("Valider la demande d'inscription")}
            //     action={() =>
            //       portal((close) => (
            //         <ChargePointsApplicationAcceptDialog
            //           application={application}
            //           companyId={companyId}
            //           onClose={close}
            //         />
            //       ))
            //     }
            //   />
            // ),
            // entity.isAdmin && application.status === ElecChargePointsApplicationStatus.Pending && (
            //   <Button
            //     captive
            //     variant="icon"
            //     icon={Cross}
            //     title={t("Refuser la demande d'inscription")}
            //     action={() =>
            //       portal((close) => (
            //         <ChargePointsApplicationRejectDialog
            //           application={application}
            //           companyId={companyId}
            //           onClose={close}
            //         />
            //       ))
            //     }
            //   />
            // ),
          ])
        ),
      ]}
    />
  );
};

export default ChargePointsApplicationsTable;