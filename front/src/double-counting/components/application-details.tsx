import { Fragment, useState } from "react"
import { useTranslation, Trans } from "react-i18next"
import { Admin, DoubleCountingStatus as DCStatus } from "../types"
import { Col, LoaderOverlay } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { Button, DownloadLink } from "common/components/button"
import * as api from "../api"
import { Confirm, Dialog } from "common/components/dialog"
import { Entity, EntityType } from "carbure/types"
import {
  Return,
  Download,
  Check,
  Cross,
  Save,
  AlertCircle,
} from "common/components/icons"
import { Alert } from "common/components/alert"
import { useNotify } from "common/components/notifications"
import DoubleCountingStatus from "./dc-status"
import {
  SourcingAggregationTable,
  SourcingTable,
  ProductionTable,
  StatusTable,
} from "./dc-tables"
import { FileInput } from "common/components/input"
import { useMutation, useQuery } from "common/hooks/async"
import { usePortal } from "common/components/portal"
import { formatDate } from "common/utils/formatters"

export type DoubleCountingDialogProps = {
  applicationID: number
  entity: Entity
  onClose: () => void
}

export const DoubleCountingDialog = ({
  entity,
  applicationID,
  onClose,
}: DoubleCountingDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const portal = usePortal()

  const [focus, setFocus] = useState("aggregated_sourcing")
  const [quotas, setQuotas] = useState<Record<string, number>>({})

  const application = useQuery(api.getDoubleCountingApplication, {
    key: "dc-application",
    params: [applicationID],

    onSuccess: (application) => {
      const applicationData = application.data.data
      if (applicationData === undefined) {
        setQuotas({})
        return
      }

      // automatically set the quotas to the asked value the first time the dossier is opened
      const quotas: Record<string, number> = {}
      applicationData.production.forEach((prod) => {
        quotas[prod.id] =
          prod.approved_quota >= 0 ? prod.approved_quota : prod.requested_quota
      })
      setQuotas(quotas)
    },
  })

  const approveQuotas = useMutation(api.approveDoubleCountingQuotas, {
    invalidates: ["dc-application"],
  })

  const approveApplication = useMutation(api.approveDoubleCountingApplication, {
    invalidates: ["dc-application"],
  })

  const rejectApplication = useMutation(api.rejectDoubleCountingApplication, {
    invalidates: ["dc-application"],
  })

  const uploadDecision = useMutation(api.uploadDoubleCountingDecision, {
    invalidates: ["dc-application"],
  })

  const applicationData = application.result?.data.data
  const dcaStatus = applicationData?.status ?? DCStatus.Pending

  let approved = false
  if (entity?.name === Admin.DGEC) {
    approved = applicationData?.dgec_validated ?? false
  } else if (entity?.name === Admin.DGDDI) {
    approved = applicationData?.dgddi_validated ?? false
  } else if (entity?.name === Admin.DGPE) {
    approved = applicationData?.dgpe_validated ?? false
  }

  const isAdmin = entity?.entity_type === EntityType.Administration
  const isAccepted = dcaStatus === DCStatus.Accepted
  const isDone = approved || dcaStatus === DCStatus.Rejected
  const hasQuotas = !applicationData?.production.some(
    (p) => p.approved_quota === -1
  )
  const isReady = isAdmin ? true : applicationData?.dgec_validated

  const productionSite = applicationData?.production_site ?? "N/A"
  const producer = applicationData?.producer.name ?? "N/A"
  const user = applicationData?.producer_user ?? "N/A"
  const creationDate = applicationData?.created_at
    ? formatDate(applicationData.created_at)
    : "N/A"

  const documentationFile = applicationData?.documents.find(
    (doc) => doc.file_type === "SOURCING"
  )
  const decisionFile = applicationData?.documents.find(
    (doc) => doc.file_type === "DECISION"
  )

  const excelURL =
    applicationData &&
    `/api/v3/doublecount/admin/application?dca_id=${applicationData.id}&export=true`
  const documentationURL =
    documentationFile &&
    `/api/v3/doublecount/admin/download-documentation?dca_id=${applicationData!.id
    }&file_id=${documentationFile.id}`
  const decisionURL =
    decisionFile &&
    `/api/v3/doublecount/admin/download-decision?dca_id=${applicationData!.id
    }&file_id=${decisionFile.id}`

  async function submitQuotas() {
    if (
      !applicationData ||
      !entity ||
      entity?.entity_type !== EntityType.Administration
    ) {
      return
    }

    const done = await approveQuotas.execute(
      applicationData.id,
      Object.keys(quotas).map((id) => [parseInt(id), quotas[id]])
    )

    if (done) {
      notify(t("Quotas mis à jour."), { variant: "success" })
    } else {
      notify(t("Impossible de mettre à jour les quotas."), {
        variant: "danger",
      })
    }
  }

  async function submitAccept() {
    portal((close) => (
      <Confirm
        variant="success"
        title={t("Accepter dossier")}
        description={t("Voulez-vous vraiment accepter ce dossier double comptage")} // prettier-ignore
        confirm={t("Accepter")}
        icon={Check}
        onClose={close}
        onConfirm={async () => {
          if (applicationData) {
            await approveApplication.execute(entity.id, applicationData.id)
          }
        }}
      />
    ))
  }

  async function submitReject() {
    portal((close) => (
      <Confirm
        variant="danger"
        title={t("Refuser dossier")}
        description={t("Voulez-vous vraiment refuser ce dossier double comptage")} // prettier-ignore
        confirm={t("Refuser")}
        icon={Cross}
        onClose={close}
        onConfirm={async () => {
          if (applicationData) {
            await rejectApplication.execute(entity.id, applicationData.id)
          }
        }}
      />
    ))
  }

  async function submitDecision(decision: File | undefined) {
    if (decision) {
      await uploadDecision.execute(applicationID, decision)
    }
  }

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <DoubleCountingStatus big status={dcaStatus} />
        <h1>{t("Dossier double comptage")} </h1>
      </header>

      <main>
        <section>
          <p>
            <Trans
              values={{ producer, productionSite, creationDate, user }}
              defaults="Pour le site de production <b>{{ productionSite }}</b> de <b>{{ producer }}</b>, soumis par <b>{{ user }}</b> le <b>{{ creationDate }}</b>"
            />
          </p>
        </section>

        {!isReady && (
          <section>
            <Alert variant="warning" icon={AlertCircle}>
              <Trans>Dossier en attente de validation par la DGEC</Trans>
            </Alert>
          </section>
        )}

        <section>
          <Tabs
            tabs={[
              { key: "aggregated_sourcing", label: t("Approvisionnement") },
              { key: "sourcing", label: t("Approvisionnement (détaillé)") },
              { key: "production", label: t("Production") },
              { key: "status", label: t("Statut") },
            ]}
            focus={focus}
            onFocus={setFocus}
          />
        </section>

        {focus === "aggregated_sourcing" && (
          <SourcingAggregationTable
            sourcing={applicationData?.aggregated_sourcing ?? []}
          />
        )}

        {focus === "sourcing" && (
          <SourcingTable sourcing={applicationData?.sourcing ?? []} />
        )}

        {focus === "production" && (
          <ProductionTable
            done={isDone}
            production={applicationData?.production ?? []}
            entity={entity}
            quotas={quotas}
            setQuotas={setQuotas}
          />
        )}

        {focus === "status" && <StatusTable application={applicationData} />}
      </main>

      <footer>
        <Col style={{ gap: "var(--spacing-xs)", marginRight: "auto" }}>
          <DownloadLink
            href={excelURL ?? "#"}
            label={t("Télécharger le dossier au format excel")}
          />
          <DownloadLink
            href={documentationURL ?? "#"}
            label={t("Télécharger la description de l'activité")}
          />
          {decisionURL && (
            <DownloadLink
              href={decisionURL ?? "#"}
              label={t("Télécharger la décision de l'administration")}
            />
          )}
        </Col>

        {isAdmin && isAccepted && !decisionFile && (
          <FileInput
            loading={uploadDecision.loading}
            icon={Download}
            value={undefined}
            onChange={submitDecision}
            placeholder={t("Mettre en ligne la décision")}
          />
        )}

        {!isDone && !application.loading && (
          <Fragment>
            {isAdmin && (
              <Button
                loading={approveQuotas.loading}
                variant="primary"
                icon={Save}
                action={submitQuotas}
              >
                <Trans>Enregistrer</Trans>
              </Button>
            )}

            <Button
              loading={approveQuotas.loading}
              disabled={!isReady || !hasQuotas}
              variant="success"
              icon={Check}
              action={submitAccept}
            >
              <Trans>Accepter</Trans>
            </Button>
            <Button
              loading={rejectApplication.loading}
              disabled={!isReady}
              variant="danger"
              icon={Cross}
              action={submitReject}
            >
              <Trans>Refuser</Trans>
            </Button>
          </Fragment>
        )}
        <Button icon={Return} action={onClose}>
          <Trans>Retour</Trans>
        </Button>
      </footer>

      {application.loading && <LoaderOverlay />}
    </Dialog>
  )
}
