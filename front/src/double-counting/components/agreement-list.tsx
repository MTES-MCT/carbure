import { Fragment, useState } from "react"
import { useTranslation, Trans } from "react-i18next"
import { DoubleCounting } from "../types"
import { ActionBar, LoaderOverlay } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import Table, { Column, Cell } from "common/components/table"
import { Alert } from "common/components/alert"
import { AlertCircle, Upload } from "common/components/icons"
import { DoubleCountingDialog } from "./agreement-details"
import { usePortal } from "common/components/portal"
import { Entity } from "carbure/types"
import DoubleCountingStatus from "./dc-status"
import * as api from "../api"
import { useQuery } from "common/hooks/async"
import { formatDate, formatDateYear } from "common/utils/formatters"
import Button from "common/components/button"
import DoubleCountingFilesCheckerDialog from "./files-checker/files-checker-dialog"
import FilesCheckerUploadButton from "./files-checker/upload-button"

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

  const columns: Column<DoubleCounting>[] = [
    {
      header: t("Statut"),
      cell: (a) => <DoubleCountingStatus status={a.status} />,
    },
    { header: t("Producteur"), cell: (a) => <Cell text={a.producer.name} /> },
    { header: t("N° d'agrément"), cell: (a) => <Cell text={a.agreement_id} /> },
    {
      header: t("Site de production"),
      cell: (a) => <Cell text={a.production_site} />,
    },
    {
      header: t("Période de validité"),
      cell: (a) => (
        <Cell
          text={`${formatDateYear(a.period_start)} - ${formatDateYear(a.period_end)}`} // prettier-ignore
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
      <ActionBar>
        <Tabs
          focus={tab}
          onFocus={setTab}
          tabs={[
            { key: "pending", label: t("En attente") },
            { key: "accepted", label: t("Accepté") },
            { key: "expired", label: t("Expiré") },
            { key: "rejected", label: t("Refusé") },
          ]}
        />

        <FilesCheckerUploadButton />
      </ActionBar>
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
