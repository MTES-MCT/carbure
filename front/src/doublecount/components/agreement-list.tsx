import { Fragment, useState, useEffect } from "react"
import { useTranslation, Trans } from "react-i18next"
import { DoubleCounting } from "../types"
import { LoaderOverlay } from "common/components"
import Tabs from "common/components/tabs"
import Table, { Column } from "common/components/table"
import { padding } from "transactions/components/list-columns"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { formatDate, YEAR_ONLY } from "settings/components/common"
import { DoubleCountingPrompt } from "./agreement-details"
import { prompt } from "common/components/dialog"
import { EntitySelection } from "carbure/hooks/use-entity"
import useAPI from "common/hooks/use-api"
import DoubleCountingStatus from './dc-status'
import * as api from "../api"

type AgreementListProps = {
  entity: EntitySelection
  year: number
}

const AgreementList = ({ entity, year }: AgreementListProps) => {
  const { t } = useTranslation()
  const [tab, setTab] = useState("pending")

  const [agreements, getAgreements] = useAPI(api.getAllDoubleCountingAgreements)

  useEffect(() => {
    getAgreements(year)
  }, [getAgreements, year])

  const tabs = [
    { key: "pending", label: t("En attente") },
    { key: "accepted", label: t("Accepté") },
    { key: "expired", label: t("Expiré") },
    { key: "rejected", label: t("Refusé") },
  ]

  const columns: Column<DoubleCounting>[] = [
    padding,
    { header: t("Statut"), render: (a) => <DoubleCountingStatus status={a.status} /> },
    { header: t("Producteur"), render: (a) => a.producer.name },
    { header: t("Site de production"), render: (a) => a.production_site },
    {
      header: t("Période de validité"),
      render: (a) =>
        `${formatDate(a.period_start, YEAR_ONLY)} - ${formatDate(
          a.period_end,
          YEAR_ONLY
        )}`,
    },
    {
      header: t("Date de soumission"),
      render: (a) => formatDate(a.creation_date),
    },
    padding,
  ]

  const agreementRowMapper = (agreement: DoubleCounting) => ({
    value: agreement,
    onClick: async () => {
      await prompt((resolve) => (
        <DoubleCountingPrompt
          entity={entity}
          agreementID={agreement.id}
          onResolve={resolve}
        />
      ))

      getAgreements(year)
    },
  })

  if (agreements.data === null) return <LoaderOverlay />

  const { pending, progress, accepted, expired, rejected } = agreements.data

  const allPendingCount = pending.count + progress.count
  const allPending = progress.agreements.concat(pending.agreements)

  return (
    <Fragment>
      <Tabs tabs={tabs} focus={tab} onFocus={setTab} />

      {tab === "pending" && (
        <Fragment>
          {allPendingCount === 0 && (
            <Alert level="warning" icon={AlertCircle}>
              <Trans>Aucun dossier en attente trouvé</Trans>
            </Alert>
          )}

          {allPendingCount > 0 && (
            <Table
              columns={columns}
              rows={allPending.map(agreementRowMapper)}
            />
          )}
        </Fragment>
      )}

      {tab === "accepted" && (
        <Fragment>
          {accepted.count === 0 && (
            <Alert level="warning" icon={AlertCircle}>
              <Trans>Aucun dossier accepté trouvé</Trans>
            </Alert>
          )}

          {accepted.count > 0 && (
            <Table
              columns={columns}
              rows={accepted.agreements.map(agreementRowMapper)}
            />
          )}
        </Fragment>
      )}

      {tab === "expired" && (
        <Fragment>
          {expired.count === 0 && (
            <Alert level="warning" icon={AlertCircle}>
              <Trans>Aucun dossier expiré trouvé</Trans>
            </Alert>
          )}

          {expired.count > 0 && (
            <Table
              columns={columns}
              rows={expired.agreements.map(agreementRowMapper)}
            />
          )}
        </Fragment>
      )}

      {tab === "rejected" && (
        <Fragment>
          {rejected.count === 0 && (
            <Alert level="warning" icon={AlertCircle}>
              <Trans>Aucun dossier refusé trouvé</Trans>
            </Alert>
          )}

          {rejected.count > 0 && (
            <Table
              columns={columns}
              rows={rejected.agreements.map(agreementRowMapper)}
            />
          )}
        </Fragment>
      )}

      {agreements.loading && <LoaderOverlay />}
    </Fragment>
  )
}

export default AgreementList
