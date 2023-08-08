import { Entity } from "carbure/types"
import { Alert } from "common/components/alert"
import HashRoute from "common/components/hash-route"
import { AlertCircle } from "common/components/icons"
import { ActionBar, LoaderOverlay } from "common/components/scaffold"
import Table, { Cell, Column } from "common/components/table"
import Tabs from "common/components/tabs"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { Fragment, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../api"
import { DoubleCountingApplicationSnapshot, DoubleCountingApplicationOverview } from "../types"
import { ApplicationDetailsDialog } from "./application-details-dialog"
import ApplicationStatus from "./application-status"
import FilesCheckerUploadButton from "./files-checker/upload-button"
import NoResult from "common/components/no-result"
import useEntity from "carbure/hooks/entity"

type ApplicationListProps = {
  snapshot: DoubleCountingApplicationSnapshot | undefined
}

const ApplicationList = ({ snapshot = defaultCount }: ApplicationListProps) => {
  const { t } = useTranslation()
  const [tab, setTab] = useState("pending")
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const applicationsResponse = useQuery(api.getAllDoubleCountingApplications, {
    key: "dc-applications",
    params: [entity.id],
  })

  const columns: Column<DoubleCountingApplicationOverview>[] = [
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

  const applications = applicationsResponse.result?.data.data

  function showApplicationDialog(application: DoubleCountingApplicationOverview) {
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

      <Fragment>
        {!applications || (tab === "pending" && applications.pending.length === 0) || (tab === "rejected" && applications.rejected.length === 0)
          ?
          <NoResult label={t("Aucun dossier trouvé")} loading={applicationsResponse.loading} />
          : <Table
            loading={applicationsResponse.loading}
            columns={columns}
            rows={tab === "pending" ? applications?.pending : applications?.rejected}
            onAction={showApplicationDialog}
          />
        }

      </Fragment>




    </section>
    <HashRoute
      path="application/:id"
      element={<ApplicationDetailsDialog />}
    />

  </>
  )
}

export default ApplicationList

const defaultCount = {
  applications_pending: 0,
  applications_rejected: 0
}
