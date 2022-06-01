import { Fragment, useState } from "react"
import { useTranslation, Trans } from "react-i18next"
import { DoubleCounting } from "../types"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Tabs from "common-v2/components/tabs"
import Table, { Column, Cell } from "common-v2/components/table"
import { Alert } from "common-v2/components/alert"
import { AlertCircle } from "common-v2/components/icons"
import { formatDate, YEAR_ONLY } from "settings/components/common"
import { DoubleCountingDialog } from "./agreement-details"
import { usePortal } from "common-v2/components/portal"
import { Entity } from "carbure/types"
import DoubleCountingStatus from "./dc-status"
import * as api from "../api"
import { useQuery } from "common-v2/hooks/async"

type AgreementListProps = {
  entity: Entity
  year: number
}

const AgreementList = ({ entity, year }: AgreementListProps) => {
  const { t } = useTranslation()
  const [tab, setTab] = useState("pending")
  const portal = usePortal()

  const agreements = useQuery(api.getAllDoubleCountingAgreements, {
    key: "dc-agreements",
    params: [year],
  })

  const tabs = [
    { key: "pending", label: t("En attente") },
    { key: "accepted", label: t("Accepté") },
    { key: "expired", label: t("Expiré") },
    { key: "rejected", label: t("Refusé") },
  ]

  const columns: Column<DoubleCounting>[] = [
    {
      header: t("Statut"),
      cell: (a) => <DoubleCountingStatus status={a.status} />,
    },
    { header: t("Producteur"), cell: (a) => <Cell text={a.producer.name} /> },
    {
      header: t("Site de production"),
      cell: (a) => <Cell text={a.production_site} />,
    },
    {
      header: t("Période de validité"),
      cell: (a) => (
        <Cell
          text={`${formatDate(a.period_start, YEAR_ONLY)} - ${formatDate(
            a.period_end,
            YEAR_ONLY
          )}`}
        />
      ),
    },
    {
      header: t("Date de soumission"),
      cell: (a) => formatDate(a.creation_date),
    },
  ]

  const agreementsData = agreements.result?.data.data
  if (agreementsData === undefined) return <LoaderOverlay />

  const { pending, progress, accepted, expired, rejected } = agreementsData

  const allPendingCount = pending.count + progress.count
  const allPending = progress.agreements.concat(pending.agreements)

  function showAgreementDialog(agreement: DoubleCounting) {
    portal((close) => (
      <DoubleCountingDialog
        entity={entity}
        agreementID={agreement.id}
        onClose={close}
      />
    ))
  }

  return (
    <section>
      <Tabs tabs={tabs} focus={tab} onFocus={setTab} />

      {tab === "pending" && (
        <Fragment>
          {allPendingCount === 0 && (
            <Alert
              variant="warning"
              icon={AlertCircle}
              loading={agreements.loading}
            >
              <Trans>Aucun dossier en attente trouvé</Trans>
            </Alert>
          )}

          {allPendingCount > 0 && (
            <Table
              loading={agreements.loading}
              columns={columns}
              rows={allPending}
              onAction={showAgreementDialog}
            />
          )}
        </Fragment>
      )}

      {tab === "accepted" && (
        <Fragment>
          {accepted.count === 0 && (
            <Alert
              variant="warning"
              icon={AlertCircle}
              loading={agreements.loading}
            >
              <Trans>Aucun dossier accepté trouvé</Trans>
            </Alert>
          )}

          {accepted.count > 0 && (
            <Table
              loading={agreements.loading}
              columns={columns}
              rows={accepted.agreements}
              onAction={showAgreementDialog}
            />
          )}
        </Fragment>
      )}

      {tab === "expired" && (
        <Fragment>
          {expired.count === 0 && (
            <Alert
              variant="warning"
              icon={AlertCircle}
              loading={agreements.loading}
            >
              <Trans>Aucun dossier expiré trouvé</Trans>
            </Alert>
          )}

          {expired.count > 0 && (
            <Table
              loading={agreements.loading}
              columns={columns}
              rows={expired.agreements}
              onAction={showAgreementDialog}
            />
          )}
        </Fragment>
      )}

      {tab === "rejected" && (
        <Fragment>
          {rejected.count === 0 && (
            <Alert
              variant="warning"
              icon={AlertCircle}
              loading={agreements.loading}
            >
              <Trans>Aucun dossier refusé trouvé</Trans>
            </Alert>
          )}

          {rejected.count > 0 && (
            <Table
              loading={agreements.loading}
              columns={columns}
              rows={rejected.agreements}
              onAction={showAgreementDialog}
            />
          )}
        </Fragment>
      )}
    </section>
  )
}

export default AgreementList
