import HashRoute from "common/components/hash-route"
import { NoResult } from "common/components/no-result2"
import { ActionBar, Content } from "common/components/scaffold"
import { Cell, Column, Table } from "common/components/table2"
import { Tabs } from "common/components/tabs2"
import { useQuery } from "common/hooks/async"
import { formatDate, formatDateYear } from "common/utils/formatters"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router"
import * as api from "../../api"
import {
  DoubleCountingApplicationOverview,
  DoubleCountingApplicationSnapshot,
} from "../../../double-counting/types"
import { ApplicationDetailsDialog } from "./application-details-dialog"
import ApplicationStatus from "../../../double-counting/components/application-status"
import { usePrivateNavigation } from "common/layouts/navigation"
import { AgreementFilters } from "../../filters"
import {
  AgreementFilter,
  ApplicationListQueryBuilder,
  ApplicationOrder,
} from "double-counting-admin/types"
import { useQueryBuilder } from "common/hooks/query-builder-2"

type ApplicationListProps = {
  snapshot: DoubleCountingApplicationSnapshot | undefined
}

const ApplicationList = ({ snapshot = defaultCount }: ApplicationListProps) => {
  const { t } = useTranslation()
  usePrivateNavigation(t("En attente"))

  const [tab, setTab] = useState("pending")
  const navigate = useNavigate()
  const location = useLocation()

  const { state, actions, query } = useQueryBuilder<
    ApplicationListQueryBuilder["config"]
  >({ status: tab })

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
      key: ApplicationOrder.certificate_id,
    },
    {
      header: t("Producteur"),
      cell: (a) => <Cell text={a.producer.name} />,
      key: ApplicationOrder.producer,
    },
    {
      header: t("Site de production"),
      cell: (a) => <Cell text={a.production_site.name} />,
      key: ApplicationOrder.production_site,
    },
    {
      header: t("Validité"),
      key: ApplicationOrder.valid_until,
      cell: (a) => (
        <Cell
          text={`${formatDateYear(a.period_start)}-${formatDateYear(a.period_end)}`}
        />
      ),
    },
    {
      header: t("Date de soumission"),
      cell: (a) => <Cell text={formatDate(a.created_at)} />,
      key: ApplicationOrder.created_at,
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
      <ActionBar>
        <Tabs
          focus={tab}
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
      </ActionBar>

      <Content>
        <AgreementFilters
          filters={CLIENT_FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getAgreementFilter}
        />

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
              tab === "pending" ? applications?.pending : applications?.rejected
            }
            onAction={showApplicationDialog}
            order={state.order}
            onOrder={actions.setOrder}
          />
        )}
      </Content>
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
