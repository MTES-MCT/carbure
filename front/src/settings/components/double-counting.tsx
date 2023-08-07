import useEntity, { useRights } from "carbure/hooks/entity"
import { UserRole } from "carbure/types"
import { Alert } from "common/components/alert"
import { AlertCircle, Plus } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { LoaderOverlay, Panel } from "common/components/scaffold"
import Table, { Cell } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatDate, formatDateYear } from "common/utils/formatters"
import ApplicationStatus from "double-counting/components/application-status"
import { DoubleCountingApplication } from "double-counting/types"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/double-counting"
import DoubleCountingApplicationDialog from "./double-counting-dialog"
import DoubleCountingUploadDialog from "./double-counting-upload"
import Button from "common/components/button"

const DoubleCountingSettings = () => {
  const { t } = useTranslation()
  const rights = useRights()
  const entity = useEntity()
  const portal = usePortal()

  const applications = useQuery(api.getDoubleCountingApplications, {
    key: "dc-applications",
    params: [entity.id],
  })

  const applicationsData = applications.result?.data.data ?? []
  const isEmpty = applicationsData.length === 0
  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  function showApplicationDialog(dc: DoubleCountingApplication) {
    portal((resolve) => (
      <DoubleCountingApplicationDialog
        entity={entity}
        applicationID={dc.id}
        onClose={resolve}
      />
    ))
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
          <Trans>Dossiers double comptage</Trans>
        </h1>
        {canModify && (
          <Button
            asideX
            variant="primary"
            icon={Plus}
            action={showUploadDialog}
            label={t("Envoyer un dossier double comptage")}
          />
        )}
      </header>

      {isEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun dossier double comptage trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isEmpty && (
        <Table
          rows={applicationsData}
          onAction={showApplicationDialog}
          columns={[
            {
              header: t("Statut"),
              cell: (dc) => <ApplicationStatus status={dc.status} />,
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
              header: t("Date de soumission"),
              cell: (dc) => <Cell text={formatDate(dc.created_at)} />,
            },
          ]}
        />
      )}

      {applications.loading && <LoaderOverlay />}
    </Panel>
  )
}

export default DoubleCountingSettings
