import useEntity from "carbure/hooks/entity"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Check, Cross, Download, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { Grid, LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell, actionColumn } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatDate, formatNumber, formatPeriod } from "common/utils/formatters"
import * as apiAdmin from "elec-admin/api"
import ElecChargePointsFileUpload from "elec/components/charge-points/upload-dialog"
import { ElecChargePointsApplication, ElecChargePointsApplicationStatus, ElecChargePointsSnapshot, ElecMeterReadingsApplication, ElecMeterReadingsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import * as apiCpo from "elec/api-cpo"
import { elecMeterReadingsApplications } from "elec/__test__/data"

import { compact } from "common/utils/collection"
import ChargePointsApplicationAcceptDialog from "elec-admin/components/charge-points/accept-dialog"
import ChargePointsApplicationRejectDialog from "elec-admin/components/charge-points/reject-dialog"
import { useMatch } from "react-router-dom"
import ApplicationStatus from "./application-status"
import ElecMeterReadingsFileUpload from "./upload-dialog"
import MeterReadingsApplicationAcceptDialog from "elec-admin/components/meter-readings/accept-dialog"
import MeterReadingsApplicationRejectDialog from "elec-admin/components/meter-readings/reject-dialog"

const ElecMeterReadingsSettings = ({ companyId }: { companyId: number }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const { isCPO } = entity
  const matchStatus = useMatch("/org/:entity/:view/*")


  const api = matchStatus?.params.view === "entities" ? apiAdmin : apiCpo
  const portal = usePortal()

  const applicationsResponse = useQuery(api.getMeterReadingsApplications, {
    key: "meter-readings-applications",
    params: [entity.id, companyId],
  })

  const applications = applicationsResponse.result?.data.data ?? []
  // const applications = elecMeterReadingsApplications // TEST with applications
  const isEmpty = applications.length === 0

  const currentDate = new Date()
  const currentQuarter = currentDate.getMonth() < 3 ? 1 : currentDate.getMonth() < 6 ? 2 : currentDate.getMonth() < 9 ? 3 : 4
  const currentYear = currentDate.getFullYear()
  const quarterString = t("T{{quarter}} {{year}}", { quarter: currentQuarter, year: currentYear })

  function showUploadDialog() {
    const pendingApplicationAlreadyExists = applications.filter(app => app.status === ElecMeterReadingsApplicationStatus.Pending && app.quarter === currentQuarter).length > 0
    portal((resolve) => (
      <ElecMeterReadingsFileUpload onClose={resolve} pendingApplicationAlreadyExists={pendingApplicationAlreadyExists} quarter={currentQuarter} year={currentYear} companyId={companyId} />
    ))
  }



  const downloadMeterReadingsApplication = (application: ElecMeterReadingsApplication) => {
    return api.downloadMeterReadingsApplicationDetails(entity.id, companyId, application.id)
  }

  return (
    <Panel id="elec-meter-readings">
      <header>
        <h1>
          {t("Relevés trimestriels")}
        </h1>

        {isCPO && (
          <Button
            asideX={true}
            variant="primary"
            icon={Plus}
            action={showUploadDialog}
            label={t("Transmettre mes relevés trimestriels {{quarter}}", { quarter: quarterString })}
          />
        )}
        {/* {applicationsSnapshot.charge_point_count > 0 &&
          <Button
            asideX={!isCPO}
            variant="secondary"
            icon={Download}
            action={downloadChargePoints}
            label={t("Exporter les points de recharge")}
          />
        } */}
      </header>



      {isEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun relevé trimestriel trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isEmpty && (
        <>

          <Table
            rows={applications}
            columns={[
              {
                header: t("Statut"),
                cell: (application) => <ApplicationStatus status={application.status} />,
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
              {
                header: t("Points de recharge"),
                cell: (application) => (
                  <Cell
                    text={`${formatNumber(application.charge_point_count)}`}
                  />
                ),
              },
              {
                header: t("kwh renouvelables"),
                cell: (application) => (
                  <Cell
                    text={`${formatNumber(Math.round(application.energy_total))}` + " kWh"}
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
                    action={() => downloadMeterReadingsApplication(application)}
                  />,
                  entity.isAdmin && application.status === ElecMeterReadingsApplicationStatus.Pending && <Button
                    captive
                    variant="icon"
                    icon={Check}
                    title={t("Valider les relevés trimestriels")}
                    action={() => portal((close) => (
                      <MeterReadingsApplicationAcceptDialog application={application} companyId={companyId} onClose={close} />
                    ))}
                  />,
                  entity.isAdmin && application.status === ElecMeterReadingsApplicationStatus.Pending && <Button
                    captive
                    variant="icon"
                    icon={Cross}
                    title={t("Refuser la demande d'inscription")}
                    action={() => portal((close) => (
                      <MeterReadingsApplicationRejectDialog application={application} companyId={companyId} onClose={close} />
                    ))}
                  />

                ])
              ),

            ]}
          />
        </>


      )}

      {applicationsResponse.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default ElecMeterReadingsSettings


