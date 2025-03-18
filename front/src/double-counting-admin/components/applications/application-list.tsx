import useEntity from "common/hooks/entity"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"
import { ActionBar } from "common/components/scaffold"
import Table, { Cell, Column } from "common/components/table"
import Tabs from "common/components/tabs"
import { useQuery } from "common/hooks/async"
import { formatDate, formatDateYear } from "common/utils/formatters"
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
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { AgreementFilters } from "../../filters"
import { AgreementFilter, AgreementOrder } from "double-counting-admin/types"

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
  const currentYear = new Date().getFullYear()

  const [state, actions] = useCBQueryParamsStore<string, undefined>(
    entity,
    currentYear,
    tab
  )
  const query = useCBQueryBuilder<AgreementOrder[], string, undefined>(state)
  const applicationsResponse = useQuery(api.getDoubleCountingApplicationList, {
    key: "dc-applications",
    params: [query],
  })

  const getAgreementFilter = (filter: AgreementFilter) => {
    return api.getApplicationFilters(filter, query)
  }

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
      header: t("Validité"),
      key: "valid_until",
      cell: (a) => (
        <Cell
          text={`${formatDateYear(a.period_start)}-${formatDateYear(a.period_end)}`}
        />
      ),
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

        <AgreementFilters
          filters={CLIENT_FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getAgreementFilter}
        />

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

const CLIENT_FILTERS = [
  AgreementFilter.Certificate_id,
  AgreementFilter.Producers,
  AgreementFilter.ProductionSites,
]

export default ApplicationList

const defaultCount = {
  applications_pending: 0,
  applications_rejected: 0,
}
