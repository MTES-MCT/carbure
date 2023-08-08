import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import Table, { Cell, Column } from "common/components/table"
import { Dialog } from "common/components/dialog"
import { Button } from "common/components/button"
import { AlertCircle, Return } from "common/components/icons"
import { formatDateYear, formatNumber } from "common/utils/formatters"
import { DoubleCountingAgreementOverview, QuotaDetails, DoubleCountingAgreementsSnapshot, AgreementStatus } from "../types"
import * as api from "../api"
import { usePortal } from "common/components/portal"
import Alert from "common/components/alert"
import { useState } from "react"
import { ActionBar, LoaderOverlay } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import Tag, { TagVariant } from "common/components/tag"
import AgreementStatusTag from "./agreement-status"
import { ApplicationDetailsDialog } from "./application-details-dialog"
import { useLocation, useNavigate } from "react-router-dom"
import { ta } from "date-fns/locale"
import useEntity from "carbure/hooks/entity"
import { AgreementDetailsDialog } from "./agreement-details-dialog"
import HashRoute from "common/components/hash-route"
import NoResult from "common/components/no-result"


const AgreementList = ({ snapshot = defaultCount }: { snapshot: DoubleCountingAgreementsSnapshot | undefined }) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const year = new Date().getFullYear()
  const [tab, setTab] = useState("active")
  const entity = useEntity()
  const navigate = useNavigate()
  const location = useLocation()

  const agreementsResponse = useQuery(api.getAgreementList, {
    key: "dc-agreements",
    params: [entity.id],
  })


  const columns: Column<DoubleCountingAgreementOverview>[] = [
    {
      header: t("Statut"),
      cell: (a) => <AgreementStatusTag status={a.status} />,
    },
    {
      header: t("N° d'agrément"),
      cell: (a) => (
        <span>
          {a.certificate_id}
        </span>
      ),
    },
    { header: t("Producteur"), cell: (a) => <Cell text={a.producer} /> },
    {
      header: t("Site de production"),
      cell: (a) => <Cell text={a.production_site || "-"} />,
    },
    {
      header: t("Validité"),
      cell: (a) => <Cell text={`${formatDateYear(a.valid_from)}-${formatDateYear(a.valid_until)}`} />,
    },

  ]

  function showApplicationDialog(agreement: DoubleCountingAgreementOverview) {
    navigate({
      pathname: location.pathname,
      hash: `agreement/${agreement.id}`,
    })
  }

  const agreements = agreementsResponse.result?.data.data

  return (
    <>
      <section>
        <ActionBar>
          <Tabs
            focus={tab}
            variant="switcher"
            onFocus={setTab}
            tabs={[
              { key: "active", label: t("Actifs ({{count}})", { count: snapshot?.agreements_active }) },
              {
                key: "expired", label: t("Expirés ({{ count }})",
                  { count: snapshot?.agreements_expired }
                )
              },
              {
                key: "incoming", label: t("À venir ({{ count }})",
                  { count: snapshot?.agreements_incoming }
                )
              },
            ]}
          />

        </ActionBar>


        {!agreements || (tab === "active" && agreements["active"].length === 0) || (tab === "expired" && agreements.expired.length === 0) || (tab === "incoming" && agreements.incoming.length === 0) ?
          <NoResult label={t("Aucun agrément trouvé")} loading={agreementsResponse.loading} />
          : <Table
            loading={agreementsResponse.loading}
            columns={columns}
            rows={tab === "active" ? agreements.active : tab === "expired" ? agreements.expired : agreements.incoming}
            onAction={showApplicationDialog}
          />
        }


      </section>
      <HashRoute
        path="agreement/:id"
        element={<AgreementDetailsDialog />}
      />
    </>
  )
}

export default AgreementList

const defaultCount = {
  agreements_active: 0,
  agreements_expired: 0,
  agreements_incoming: 0
}
