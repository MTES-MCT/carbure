import { Fragment, useState } from "react"
import { useTranslation, Trans } from "react-i18next"
import { EntityType } from "carbure/types"
import { Admin, DoubleCountingStatus as DCStatus } from "../types"
import { Col, LoaderOverlay } from "common-v2/components/scaffold"
import Tabs from "common-v2/components/tabs"
import { Button, DownloadLink } from "common-v2/components/button"
import * as api from "../api"
import { Confirm, Dialog } from "common-v2/components/dialog"
import { Entity } from "carbure/types"
import {
  Return,
  Download,
  Check,
  Cross,
  Save,
  AlertCircle,
} from "common-v2/components/icons"
import { Alert } from "common-v2/components/alert"
import { useNotify } from "common-v2/components/notifications"
import DoubleCountingStatus from "./dc-status"
import {
  SourcingAggregationTable,
  SourcingTable,
  ProductionTable,
  StatusTable,
} from "./dc-tables"
import { FileInput } from "common-v2/components/input"
import { useMutation, useQuery } from "common-v2/hooks/async"
import { usePortal } from "common-v2/components/portal"
import { formatDate } from "common-v2/utils/formatters"

export type DoubleCountingDialogProps = {
  agreementID: number
  entity: Entity
  onClose: () => void
}

export const DoubleCountingDialog = ({
  entity,
  agreementID,
  onClose,
}: DoubleCountingDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const portal = usePortal()

  const [focus, setFocus] = useState("aggregated_sourcing")
  const [quotas, setQuotas] = useState<Record<string, number>>({})

  const agreement = useQuery(api.getDoubleCountingAgreement, {
    key: "dc-agreement",
    params: [agreementID],

    onSuccess: (agreement) => {
      const agreementData = agreement.data.data
      if (agreementData === undefined) {
        setQuotas({})
        return
      }

      // automatically set the quotas to the asked value the first time the dossier is opened
      const quotas: Record<string, number> = {}
      agreementData.production.forEach((prod) => {
        quotas[prod.id] =
          prod.approved_quota >= 0 ? prod.approved_quota : prod.requested_quota
      })
      setQuotas(quotas)
    },
  })

  const approveQuotas = useMutation(api.approveDoubleCountingQuotas, {
    invalidates: ["dc-agreement"],
  })

  const approveAgreement = useMutation(api.approveDoubleCountingAgreement, {
    invalidates: ["dc-agreement"],
  })

  const rejectAgreement = useMutation(api.rejectDoubleCountingAgreement, {
    invalidates: ["dc-agreement"],
  })

  const uploadDecision = useMutation(api.uploadDoubleCountingDecision, {
    invalidates: ["dc-agreement"],
  })

  const agreementData = agreement.result?.data.data
  const dcaStatus = agreementData?.status ?? DCStatus.Pending

  let approved = false
  if (entity?.name === Admin.DGEC) {
    approved = agreementData?.dgec_validated ?? false
  } else if (entity?.name === Admin.DGDDI) {
    approved = agreementData?.dgddi_validated ?? false
  } else if (entity?.name === Admin.DGPE) {
    approved = agreementData?.dgpe_validated ?? false
  }

  const isAdmin = entity?.entity_type === EntityType.Administration
  const isAccepted = dcaStatus === DCStatus.Accepted
  const isDone = approved || dcaStatus === DCStatus.Rejected
  const hasQuotas = !agreementData?.production.some(
    (p) => p.approved_quota === -1
  )
  const isReady = isAdmin ? true : agreementData?.dgec_validated

  const productionSite = agreementData?.production_site ?? "N/A"
  const producer = agreementData?.producer.name ?? "N/A"
  const user = agreementData?.producer_user ?? "N/A"
  const creationDate = agreementData?.creation_date
    ? formatDate(agreementData.creation_date)
    : "N/A"

  const documentationFile = agreementData?.documents.find(
    (doc) => doc.file_type === "SOURCING"
  )
  const decisionFile = agreementData?.documents.find(
    (doc) => doc.file_type === "DECISION"
  )

  const excelURL =
    agreementData &&
    `/api/v3/doublecount/admin/agreement?dca_id=${agreementData.id}&export=true`
  const documentationURL =
    documentationFile &&
    `/api/v3/doublecount/admin/download-documentation?dca_id=${
      agreementData!.id
    }&file_id=${documentationFile.id}`
  const decisionURL =
    decisionFile &&
    `/api/v3/doublecount/admin/download-decision?dca_id=${
      agreementData!.id
    }&file_id=${decisionFile.id}`

  async function submitQuotas() {
    if (
      !agreementData ||
      !entity ||
      entity?.entity_type !== EntityType.Administration
    ) {
      return
    }

    const done = await approveQuotas.execute(
      agreementData.id,
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
          if (agreementData) {
            await approveAgreement.execute(entity.id, agreementData.id)
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
          if (agreementData) {
            await rejectAgreement.execute(entity.id, agreementData.id)
          }
        }}
      />
    ))
  }

  async function submitDecision(decision: File | undefined) {
    if (decision) {
      await uploadDecision.execute(agreementID, decision)
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
            <Trans>
              Pour le site de production <b>{{ productionSite }}</b> de{" "}
              <b>{{ producer }}</b>, soumis par <b>{{ user }}</b> le{" "}
              <b>{{ creationDate }}</b>
            </Trans>
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
            sourcing={agreementData?.aggregated_sourcing ?? []}
          />
        )}

        {focus === "sourcing" && (
          <SourcingTable sourcing={agreementData?.sourcing ?? []} />
        )}

        {focus === "production" && (
          <ProductionTable
            done={isDone}
            production={agreementData?.production ?? []}
            entity={entity}
            quotas={quotas}
            setQuotas={setQuotas}
          />
        )}

        {focus === "status" && <StatusTable agreement={agreementData} />}
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
              label={t("Téléchargerla décision de l'administration")}
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

        {!isDone && !agreement.loading && (
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
              loading={rejectAgreement.loading}
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

      {agreement.loading && <LoaderOverlay />}
    </Dialog>
  )
}
