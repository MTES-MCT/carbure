import useEntity, { useRights } from "carbure/hooks/entity"
import { UserRole } from "carbure/types"
import { Alert } from "common/components/alert"
import Button from "common/components/button"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatDateYear } from "common/utils/formatters"
import ApplicationStatus from "double-counting/components/application-status"
import { DoubleCountingApplicationOverview, DoubleCountingStatus } from "double-counting/types"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "double-counting/api"
import DoubleCountingUploadDialog from "double-counting/components/upload-dialog"

const DoubleCountingSettings = () => {
  const { t } = useTranslation()
  const rights = useRights()
  const entity = useEntity()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()

  const applicationsData = useQuery(api.getDoubleCountingAgreements, {

    key: "dc-agreements",
    params: [entity.id],
  })

  const applications = applicationsData.result?.data.data ?? []
  const isEmpty = applications.length === 0
  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  function showApplicationDialog(application: DoubleCountingApplicationOverview) {
    if ([DoubleCountingStatus.Pending, DoubleCountingStatus.Rejected].includes(application.status)) {
      navigate({
        pathname: location.pathname,
        hash: `double-counting/applications/${application.id}`,
      })
    } else {
      navigate({
        pathname: location.pathname,
        hash: `double-counting/agreements/${application.agreement_id}`,
      })
    }
  }

  function showUploadDialog() {
    portal((resolve) => (
      <DoubleCountingUploadDialog onClose={resolve} />
    ))
  }

  return (
    <Panel id="double-counting">
      <header>
        <h1>
          <Trans>Agréments double comptage</Trans>
        </h1>
        {canModify && (
          <Button
            asideX
            variant="primary"
            icon={Plus}
            action={showUploadDialog}
            label={t("Envoyer une demande d'agrément")}
          />
        )}
      </header>

      {isEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun agrément double comptage trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isEmpty && (
        <Table
          rows={applications}
          onAction={showApplicationDialog}
          columns={[
            {
              header: t("Statut"),
              cell: (dc) => <ApplicationStatus status={dc.status} expirationDate={dc.period_end} />,
            },
            {
              header: t("Site de production"),
              cell: (dc) => <Cell text={dc.production_site} />,
            },
            {
              header: t("Période de validité"),
              cell: (dc) => (
                <Cell
                  text={`${formatDateYear(dc.period_start)} - ${formatDateYear(dc.period_end)}`} // prettier-ignore
                />
              ),
            },
            {
              header: t("N° d'agrément"),
              cell: (dc) => (
                <span>
                  {dc.status === DoubleCountingStatus.Rejected && (
                    <>-</>
                  )}
                  {dc.status === DoubleCountingStatus.Pending && t("En cours de traitement...")}

                  {dc.status === DoubleCountingStatus.Accepted && (
                    <>{dc.certificate_id}</>
                  )}

                </span>
              ),
            },
            {
              header: t("Quotas"),
              cell: (dc) => <Cell text={dc.quotas_progression != null ? Math.round(dc.quotas_progression * 100) + "%" : "-"} />,
            }
            // {
            //   header: t("Date de soumission"),
            //   cell: (dc) => <Cell text={formatDate(dc.created_at)} />,
            // },
          ]}
        />
      )}

      {applicationsData.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default DoubleCountingSettings
