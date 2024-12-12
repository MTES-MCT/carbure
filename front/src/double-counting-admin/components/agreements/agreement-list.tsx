import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import HashRoute from "common/components/hash-route"
import { Download } from "common/components/icons"
import NoResult from "common/components/no-result"
import { ActionBar } from "common/components/scaffold"
import Table, { Cell, Column, Order } from "common/components/table"
import Tabs from "common/components/tabs"
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

const AgreementList = ({
  snapshot = defaultCount,
}: {
  snapshot: DoubleCountingAgreementsSnapshot | undefined
}) => {
  const { t } = useTranslation()
  const [tab, setTab] = useState("active")
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()
  const [order, setOrder] = useState<Order | undefined>(undefined)
  const currentYear = new Date().getFullYear()

  const agreementsResponse = useQuery(api.getDoubleCountingAgreementList, {
    key: "dc-agreements",
    params: [entity.id, order?.column, order?.direction],
  })

  const columns: Column<DoubleCountingAgreementOverview>[] = compact([
    {
      header: t("Statut"),
      cell: (a) => <AgreementStatusTag status={a.status} />,
    },
    {
      header: t("N° d'agrément"),
      cell: (a) => <span>{a.certificate_id}</span>,
    },
    { header: t("Producteur"), cell: (a) => <Cell text={a.producer} /> },
    {
      header: t("Site de production"),
      key: "production_site",
      cell: (a) => <Cell text={a.production_site || "-"} />,
    },
    {
      header: t("Validité"),
      key: "valid_until",
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
          text={`${a.quotas_progression ? Math.round(a.quotas_progression * 100) : "-"} %`}
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
          {tab === "active" && agreements && agreements.active.length > 0 && (
            <ExportAgreementsButton />
          )}
        </ActionBar>

        {!agreements ||
        (tab === "active" && agreements["active"].length === 0) ||
        (tab === "expired" && agreements.expired.length === 0) ||
        (tab === "incoming" && agreements.incoming.length === 0) ? (
          <NoResult
            label={t("Aucun agrément trouvé")}
            loading={agreementsResponse.loading}
          />
        ) : (
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
            order={order}
            onOrder={setOrder}
          />
        )}
      </section>
      <HashRoute path="agreement/:id" element={<AgreementDetailsDialog />} />
    </>
  )
}

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
      asideX={true}
      icon={Download}
      label={t("Exporter les agréments")}
      action={() => api.downloadDoubleCountingAgreementList(entity.id)}
    />
  )
}
