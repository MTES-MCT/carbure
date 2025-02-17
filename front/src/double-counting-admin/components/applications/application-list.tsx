import useEntity from "carbure/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import { ActionBar } from "common/components/scaffold"
import Table, { Cell, Column } from "common/components/table"
import Tabs from "common/components/tabs"
import { useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { Fragment, useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import {
  DoubleCountingApplicationOverview,
  DoubleCountingApplicationSnapshot,
} from "../../../double-counting/types"
import { ApplicationDetailsDialog } from "./application-details-dialog"
import ApplicationStatus from "../../../double-counting/components/application-status"
import FilesCheckerUploadButton from "../files-checker/upload-button"
import { usePrivateNavigation } from "common/layouts/navigation"

type ApplicationListProps = {
  snapshot: DoubleCountingApplicationSnapshot | undefined
}

const ApplicationList = ({ snapshot = defaultCount }: ApplicationListProps) => {
  const { t } = useTranslation()
  usePrivateNavigation(t("En attente"))

  const [tab, setTab] = useState("pending")
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const applicationsResponse = useQuery(api.getDoubleCountingApplicationList, {
    key: "dc-applications",
    params: [entity.id],
  })

  const columns: Column<DoubleCountingApplicationOverview>[] = [
    {
      header: t("Statut"),
      cell: (a) => (
        <ApplicationStatus status={a.status} expirationDate={a.period_end} />
      ),
    },
    {
      header: t("N° d'agrément"),
      cell: (a) => <Cell text={a.certificate_id} />,
    },
    { header: t("Producteur"), cell: (a) => <Cell text={a.producer.name} /> },
    {
      header: t("Site de production"),
      cell: (a) => <Cell text={a.production_site.name} />,
    },
    {
      header: t("Date de soumission"),
      cell: (a) => <Cell text={formatDate(a.created_at)} />,
    },
  ]

  const applications = applicationsResponse.result?.data

  function showApplicationDialog(
    application: DoubleCountingApplicationOverview
  ) {
    navigate({
      pathname: location.pathname,
      hash: `application/${application.id}`,
    })
  }

  return (
    <>
      <section>
        <ActionBar>
          <Tabs
            focus={tab}
            variant="switcher"
            onFocus={setTab}
            tabs={[
              {
                key: "pending",
                label: t("En attente ({{count}})", {
                  count: snapshot?.applications_pending,
                }),
              },
              {
                key: "rejected",
                label: t("Refusé ({{ count }})", {
                  count: snapshot?.applications_rejected,
                }),
              },
            ]}
          />

          <FilesCheckerUploadButton />
        </ActionBar>

        <Fragment>
          {!applications ||
          (tab === "pending" && applications.pending.length === 0) ||
          (tab === "rejected" && applications.rejected.length === 0) ? (
            <NoResult
              label={t("Aucune demande trouvée")}
              loading={applicationsResponse.loading}
            />
          ) : (
            <Table
              loading={applicationsResponse.loading}
              columns={columns}
              rows={
                tab === "pending"
                  ? applications?.pending
                  : applications?.rejected
              }
              onAction={showApplicationDialog}
            />
          )}
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
  applications_rejected: 0,
}
