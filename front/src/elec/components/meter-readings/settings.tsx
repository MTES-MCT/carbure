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
import ElecChargingPointsFileUpload from "elec/components/charging-points/upload-dialog"
import { ElecChargingPointsApplication, ElecChargingPointsApplicationStatus, ElecChargingPointsSnapshot, ElecMeterReadingsApplication, ElecMeterReadingsApplicationStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import * as apiCpo from "elec/api-cpo"
import { elecMeterReadingsApplications } from "elec/__test__/data"

import { compact } from "common/utils/collection"
import ChargingPointsApplicationAcceptDialog from "elec-admin/components/charging-points/accept-dialog"
import ChargingPointsApplicationRejectDialog from "elec-admin/components/charging-points/reject-dialog"
import { useMatch } from "react-router-dom"
import ApplicationStatus from "./application-status"
import { c } from "msw/lib/glossary-de6278a9"
import ElecMeterReadingsFileUpload from "./upload-dialog"

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

  // const applications = applicationsResponse.result?.data.data ?? []
  const applications = elecMeterReadingsApplications // TEST with applications
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

  // function downloadChargingPoints() {
  //   api.downloadChargingPoints(entity.id, companyId)
  // }

  // const downloadChargingPointsApplication = (application: ElecChargingPointsApplication) => {
  //   return api.downloadChargingPointsApplicationDetails(entity.id, companyId, application.id)
  // }

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
        {/* {applicationsSnapshot.charging_point_count > 0 &&
          <Button
            asideX={!isCPO}
            variant="secondary"
            icon={Download}
            action={downloadChargingPoints}
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
                    text={`${formatNumber(application.charging_point_count)}`}
                  />
                ),
              },
              {
                header: t("Kwh renouvelables"),
                cell: (application) => (
                  <Cell
                    text={`${formatNumber(Math.round(application.power_total))}` + " kW"}
                  />
                ),
              },
              actionColumn<ElecMeterReadingsApplication>((application) =>
                compact([

                  // <Button
                  //   captive
                  //   variant="icon"
                  //   icon={Download}
                  //   title={t("Exporter les points de recharge")}
                  //   action={() => downloadChargingPointsApplication(application)}
                  // />,
                  // entity.isAdmin && application.status === ElecChargingPointsApplicationStatus.Pending && <Button
                  //   captive
                  //   variant="icon"
                  //   icon={Check}
                  //   title={t("Valider la demande d'inscription")}
                  //   action={() => portal((close) => (
                  //     <ChargingPointsApplicationAcceptDialog application={application} companyId={companyId} onClose={close} />
                  //   ))}
                  // />,
                  // entity.isAdmin && application.status === ElecChargingPointsApplicationStatus.Pending && <Button
                  //   captive
                  //   variant="icon"
                  //   icon={Cross}
                  //   title={t("Refuser la demande d'inscription")}
                  //   action={() => portal((close) => (
                  //     <ChargingPointsApplicationRejectDialog application={application} companyId={companyId} onClose={close} />
                  //   ))}
                  // />

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


