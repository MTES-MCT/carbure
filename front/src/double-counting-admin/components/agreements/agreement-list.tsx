import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import HashRoute from "common/components/hash-route"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { NoResult } from "common/components/no-result2"
import { Content } from "common/components/scaffold"
import { Cell, Column, Table } from "common/components/table2"
import { Tabs } from "common/components/tabs2"
import { useQuery } from "common/hooks/async"
import { formatDateYear } from "common/utils/formatters"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import {
  DoubleCountingAgreementOverview,
  DoubleCountingAgreementsSnapshot,
} from "../../../double-counting/types"
import { AgreementDetailsDialog } from "./agreement-details-dialog"
import AgreementStatusTag from "./agreement-status"
import { compact } from "common/utils/collection"
import { usePrivateNavigation } from "common/layouts/navigation"
import { AgreementFilters } from "../../filters"
import { AgreementFilter, AgreementOrder } from "double-counting-admin/types"

const AgreementList = ({
  snapshot = defaultCount,
}: {
  snapshot: DoubleCountingAgreementsSnapshot | undefined
}) => {
  const { t } = useTranslation()
  usePrivateNavigation(t("Agréments actifs"))
  const [tab, setTab] = useState("active")
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const currentYear = new Date().getFullYear()

  const [state, actions] = useCBQueryParamsStore<string, undefined>(
    entity,
    currentYear,
    tab
  )
  const query = useCBQueryBuilder<AgreementOrder[], string, undefined>(state)
  const agreementsResponse = useQuery(api.getDoubleCountingAgreementList, {
    key: "dc-agreements",
    params: [query],
  })

  const columns: Column<DoubleCountingAgreementOverview>[] = compact([
    {
      header: t("Statut"),
      cell: (a) => <AgreementStatusTag status={a.status} />,
    },
    {
      header: t("N° d'agrément"),
      cell: (a) => <Cell text={a.certificate_id} />,
      key: AgreementOrder.certificate_id,
    },
    {
      header: t("Producteur"),
      cell: (a) => <Cell text={a.producer?.name} />,
      key: AgreementOrder.producer,
    },
    {
      header: t("Site de production"),
      key: AgreementOrder.production_site,
      cell: (a) => <Cell text={a.production_site || "-"} />,
    },
    {
      header: t("Validité"),
      key: AgreementOrder.valid_until,
      cell: (a) => (
        <Cell
          text={`${formatDateYear(a.valid_from)}-${formatDateYear(a.valid_until)}`}
        />
      ),
    },
    tab === "active" && {
      header: t("Quotas") + " " + currentYear,
      cell: (a) => (
        <Cell
          text={`${a.quotas_progression ? Math.round(a.quotas_progression * 100) + "%" : "-"}`}
        />
      ),
    },
  ])

  function showApplicationDialog(agreement: DoubleCountingAgreementOverview) {
    navigate({
      pathname: location.pathname,
      hash: `agreement/${agreement.id}`,
    })
  }

  const agreements = agreementsResponse.result?.data

  const getAgrementFilter = (filter: AgreementFilter) => {
    return api.getAgrementFilters(filter, query)
  }

  return (
    <>
      {tab === "active" && agreements && agreements.active.length > 0 && (
        <ExportAgreementsButton />
      )}
      <Tabs
        focus={tab}
        onFocus={setTab}
        tabs={[
          {
            key: "active",
            label: t("Actifs ({{count}})", {
              count: snapshot?.agreements_active,
            }),
          },
          {
            key: "expired",
            label: t("Expirés ({{ count }})", {
              count: snapshot?.agreements_expired,
            }),
          },
          {
            key: "incoming",
            label: t("À venir ({{ count }})", {
              count: snapshot?.agreements_incoming,
            }),
          },
        ]}
      />
      <Content>
        <AgreementFilters
          filters={CLIENT_FILTERS}
          selected={state.filters}
          onSelect={actions.setFilters}
          getFilterOptions={getAgrementFilter}
        />
        {!agreements ||
        (tab === "active" && agreements["active"].length === 0) ||
        (tab === "expired" && agreements.expired.length === 0) ||
        (tab === "incoming" && agreements.incoming.length === 0) ? (
          <NoResult
            label={t("Aucun agrément trouvé")}
            loading={agreementsResponse.loading}
          />
        ) : (
          <>
            <Table
              loading={agreementsResponse.loading}
              columns={columns}
              rows={
                tab === "active"
                  ? agreements.active
                  : tab === "expired"
                    ? agreements.expired
                    : agreements.incoming
              }
              onAction={showApplicationDialog}
              order={state.order}
              onOrder={actions.setOrder}
            />
          </>
        )}
      </Content>
      <HashRoute path="agreement/:id" element={<AgreementDetailsDialog />} />
    </>
  )
}

const CLIENT_FILTERS = [
  AgreementFilter.Certificate_id,
  AgreementFilter.Producers,
  AgreementFilter.ProductionSites,
]

export default AgreementList

const defaultCount = {
  agreements_active: 0,
  agreements_expired: 0,
  agreements_incoming: 0,
}

export const ExportAgreementsButton = () => {
  const { t } = useTranslation()
  const entity = useEntity()
  return (
    <Button
      iconId="ri-download-line"
      onClick={() => api.downloadDoubleCountingAgreementList(entity.id)}
      asideX
    >
      {t("Exporter les agréments")}
    </Button>
  )
}
