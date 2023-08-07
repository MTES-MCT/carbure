import { Entity } from "carbure/types"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { ActionBar, LoaderOverlay } from "common/components/scaffold"
import Table, { Cell, Column } from "common/components/table"
import Tabs from "common/components/tabs"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { Fragment, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api"
import { ApplicationSnapshot, DoubleCountingApplication } from "../types"
import { DoubleCountingApplicationDialog } from "./application-details-dialog"
import ApplicationStatus from "./application-status"
import FilesCheckerUploadButton from "./files-checker/upload-button"
import HashRoute from "common/components/hash-route"
import { useLocation, useNavigate } from "react-router-dom"

type ApplicationListProps = {
  entity: Entity
  snapshot: ApplicationSnapshot | undefined
}

const ApplicationList = ({ entity, snapshot = defaultCount }: ApplicationListProps) => {
  const { t } = useTranslation()
  const [tab, setTab] = useState("pending")
  const navigate = useNavigate()
  const location = useLocation()

  const applications = useQuery(api.getAllDoubleCountingApplications, {
    key: "dc-applications",
    params: [],
  })

  const columns: Column<DoubleCountingApplication>[] = [
    {
      header: t("Statut"),
      cell: (a) => <ApplicationStatus status={a.status} />,
    },
    { header: t("N° d'agrément"), cell: (a) => <Cell text={a.agreement_id} /> },
    { header: t("Producteur"), cell: (a) => <Cell text={a.producer.name} /> },
    {
      header: t("Site de production"),
      cell: (a) => <Cell text={a.production_site} />,
    },
    {
      header: t("Date de soumission"),
      cell: (a) => (
        <Cell
          text={formatDate(a.created_at)}
        />
      ),
    }
  ]

  const applicationsData = applications.result?.data.data
  if (applicationsData === undefined) return <LoaderOverlay />

  const { pending, rejected } = applicationsData

  function showApplicationDialog(application: DoubleCountingApplication) {
    navigate({
      pathname: location.pathname,
      hash: `application/${application.id}`,
    })
  }

  return (<>
    <section>
      <ActionBar>
        <Tabs
          focus={tab}
          variant="switcher"
          onFocus={setTab}
          tabs={[
            { key: "pending", label: t("En attente ({{count}})", { count: snapshot?.applications_pending }) },
            {
              key: "rejected", label: t("Refusé ({{ count }})",
                { count: snapshot?.applications_rejected }
              )
            },
          ]}
        />

        <FilesCheckerUploadButton />
      </ActionBar>
      {tab === "pending" && (
        <Fragment>
          {snapshot.applications_pending === 0 && (
            <Alert
              variant="warning"
              icon={AlertCircle}
              loading={applications.loading}
            >
              <Trans>Aucun dossier en attente trouvé</Trans>
            </Alert>
          )}

          {snapshot.applications_pending > 0 && (
            <Table
              loading={applications.loading}
              columns={columns}
              rows={pending}
              onAction={showApplicationDialog}
            />
          )}
        </Fragment>
      )}


      {tab === "rejected" && (
        <Fragment>
          {rejected.length === 0 && (
            <Alert
              variant="warning"
              icon={AlertCircle}
              loading={applications.loading}
            >
              <Trans>Aucun dossier refusé trouvé</Trans>
            </Alert>
          )}

          {rejected.length > 0 && (
            <Table
              loading={applications.loading}
              columns={columns}
              rows={rejected}
              onAction={showApplicationDialog}
            />
          )}
        </Fragment>
      )}
    </section>
    <HashRoute
      path="application/:id"
      element={<DoubleCountingApplicationDialog />}
    />

  </>
  )
}

export default ApplicationList

const defaultCount = {
  applications_pending: 0,
  applications_rejected: 0
}
