import Button from "common/components/button"
import { Cross, Download } from "common/components/icons"
import Table, { Cell, actionColumn } from "common/components/table"
import { formatDate, formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/application-status"
import {
  ElecAuditApplicationStatus,
  ElecChargePointsApplication,
} from "elec/types"
import { useTranslation } from "react-i18next"
import { compact } from "common/utils/collection"

import { To } from "react-router-dom"
import { usePortal } from "common/components/portal"
import { Confirm } from "common/components/dialog"

interface ChargePointsApplicationsTableProps {
  applications: ElecChargePointsApplication[]
  onDownloadChargePointsApplication: (
    application: ElecChargePointsApplication
  ) => void
  onDeleteChargePointsApplication?: (id: number) => Promise<unknown>
  rowLink?: (row: ElecChargePointsApplication) => To
  loading?: boolean
  displayCpo?: boolean
}

const ChargePointsApplicationsTable: React.FC<
  ChargePointsApplicationsTableProps
> = ({
  applications,
  onDownloadChargePointsApplication,
  onDeleteChargePointsApplication,
  rowLink,
  loading,
  displayCpo = false,
}) => {
  const { t } = useTranslation()
  const portal = usePortal()

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
            [
              ElecAuditApplicationStatus.Pending,
              ElecAuditApplicationStatus.Rejected,
            ].includes(application.status) &&
              onDeleteChargePointsApplication && (
                <Button
                  captive
                  variant="icon"
                  icon={Cross}
                  title={t("Supprimer le dossier")}
                  action={() =>
                    portal((close) => (
                      <Confirm
                        variant="danger"
                        icon={Cross}
                        title={t("Supprimer le dossier")}
                        description={t(
                          "Voulez-vous supprimer ce dossier d'inscription de points de recharge ?"
                        )}
                        confirm={t("Supprimer")}
                        onConfirm={() =>
                          onDeleteChargePointsApplication(application.id)
                        }
                        onClose={close}
                      />
                    ))
                  }
                />
              ),
          ])
        ),
      ])}
    />
  )
}

export default ChargePointsApplicationsTable
