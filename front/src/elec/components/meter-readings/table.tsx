import Button from "common/components/button"
import { Cross, Download } from "common/components/icons"
import Table, { Cell, actionColumn } from "common/components/table"
import { formatNumber } from "common/utils/formatters"
import ApplicationStatus from "elec/components/application-status"
import {
  ElecAuditApplicationStatus,
  ElecMeterReadingsApplication,
} from "elec/types"
import { useTranslation } from "react-i18next"
import { compact } from "common/utils/collection"

import { To } from "react-router-dom"
import { Confirm } from "common/components/dialog"
import { usePortal } from "common/components/portal"

interface MeterReadingsApplicationsTableProps {
  applications: ElecMeterReadingsApplication[]
  onDownloadMeterReadingsApplication: (
    application: ElecMeterReadingsApplication
  ) => void
  onDeleteMeterReadingsApplication: (id: number) => Promise<unknown>
  rowLink?: (row: ElecMeterReadingsApplication) => To
  loading?: boolean
  displayCpo?: boolean
}

const MeterReadingsApplicationsTable: React.FC<
  MeterReadingsApplicationsTableProps
> = ({
  applications,
  onDownloadMeterReadingsApplication,
  onDeleteMeterReadingsApplication,
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
              text={`${formatNumber(Math.round(application.energy_total))} kWh`}
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
            application.status === ElecAuditApplicationStatus.Pending &&
              onDeleteMeterReadingsApplication && (
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
                          "Voulez-vous supprimer ce dossier d'inscription de relevés ?"
                        )}
                        confirm={t("Supprimer")}
                        onConfirm={() =>
                          onDeleteMeterReadingsApplication(application.id)
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

export default MeterReadingsApplicationsTable
