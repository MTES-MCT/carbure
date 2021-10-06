import { Fragment, useState, useEffect } from "react"
import { useTranslation, Trans } from "react-i18next"
import {
  Admin,
  DoubleCountingStatus as DCStatus,
  DoubleCountingSourcing,
  DoubleCountingProduction,
  EntityType,
  DoubleCountingDetails,
  DoubleCountingSourcingAggregation
} from "common/types"
import useAPI from "common/hooks/use-api"
import { LoaderOverlay, Box } from "common/components"
import Tabs from "common/components/tabs"
import { Input } from "common/components/input"
import { Button, AsyncButton } from "common/components/button"
import Table, { Column, Row } from "common/components/table"
import { padding } from "transactions/components/list-columns"
import * as api from "../api"
import {
  Dialog,
  DialogButtons,
  DialogTitle,
  DialogText,
  confirm,
  PromptProps,
} from "common/components/dialog"
import { EntitySelection } from "carbure/hooks/use-entity"
import styles from "settings/components/settings.module.css"
import {
  Return,
  Upload,
  Check,
  Cross,
  Save,
  AlertCircle,
} from "common/components/icons"
import { formatDate } from "settings/components/common"
import { Alert } from "common/components/alert"
import { useNotificationContext } from "common/components/notifications"
import YearTable from "./year-table"
import DoubleCountingStatus from './dc-status'
import { 
  SourcingAggregationTable,
  SourcingTable,
  ProductionTable,
  StatusTable
} from './dc-tables'

export type DoubleCountingPromptProps = PromptProps<any> & {
  agreementID: number
  entity: EntitySelection
}

export const DoubleCountingPrompt = ({
  entity,
  agreementID,
  onResolve,
}: DoubleCountingPromptProps) => {
  const { t } = useTranslation()
  const notifications = useNotificationContext()

  const [focus, setFocus] = useState("aggregated_sourcing")
  const [quotas, setQuotas] = useState<Record<string, string>>({})

  const [agreement, getAgreement] = useAPI(api.getDoubleCountingAgreement)
  const [approving, approveAgreement] = useAPI(
    api.approveDoubleCountingAgreement
  )
  const [rejecting, rejectAgreement] = useAPI(api.rejectDoubleCountingAgreement)
  const [approvingQuotas, approveQuotas] = useAPI(
    api.approveDoubleCountingQuotas
  )

  useEffect(() => {
    getAgreement(agreementID)
  }, [agreementID, getAgreement])

  useEffect(() => {
    if (agreement.data === null) {
      setQuotas({})
      return
    }

    // automatically set the quotas to the asked value the first time the dossier is opened
    const quotas: Record<string, string> = {}
    agreement.data.production.forEach((prod) => {
      quotas[prod.id] =
        prod.approved_quota >= 0
          ? `${prod.approved_quota}`
          : `${prod.requested_quota}`
    })
    setQuotas(quotas)
  }, [agreement.data])

  const dcaStatus = agreement.data?.status ?? DCStatus.Pending

  const excelURL =
    agreement.data &&
    `/api/v3/doublecount/admin/agreement?dca_id=${agreement.data.id}&export=true`
  const documentationURL =
    agreement.data &&
    agreement.data.documents[0] &&
    `/api/v3/doublecount/admin/download-documentation?dca_id=${agreement.data.id}&file_id=${agreement.data.documents[0].id}`

  let approved = false
  if (entity?.name === Admin.DGEC) {
    approved = agreement.data?.dgec_validated ?? false
  } else if (entity?.name === Admin.DGDDI) {
    approved = agreement.data?.dgddi_validated ?? false
  } else if (entity?.name === Admin.DGPE) {
    approved = agreement.data?.dgpe_validated ?? false
  }

  const isDone =
    approved || agreement.data?.status === DCStatus.Rejected
  const hasQuotas = !agreement.data?.production.some(p => p.approved_quota === -1)
  const isAdmin = entity?.entity_type === EntityType.Administration
  const isReady = isAdmin ? true : agreement.data?.dgec_validated

  const productionSite = agreement.data?.production_site ?? "N/A"
  const producer = agreement.data?.producer.name ?? "N/A"
  const user = agreement.data?.producer_user ?? "N/A"
  const creationDate = agreement.data?.creation_date
    ? formatDate(agreement.data.creation_date)
    : "N/A"

  async function submitQuotas() {
    if (
      !agreement.data ||
      !entity ||
      entity?.entity_type !== EntityType.Administration
    ) {
      return
    }

    const done = await approveQuotas(
      agreement.data.id,
      Object.keys(quotas).map((id) => [parseInt(id), parseInt(quotas[id])])
    )
    
    getAgreement(agreementID)

    if (done) {
      notifications.push({
        level: "success",
        text: t("Quotas mis à jour."),
      })
    } else {
      notifications.push({
        level: "error",
        text: t("Impossible de mettre à jour les quotas."),
      })
    }
  }

  async function submitAccept() {
    if (!agreement.data || !entity) return

    const ok = await confirm(
      t("Accepter dossier"),
      t("Voulez-vous vraiment accepter ce dossier double comptage")
    )

    if (!ok) return

    await approveAgreement(entity.id, agreement.data.id)

    onResolve()
  }

  async function submitReject() {
    if (!agreement.data || !entity) return

    const ok = await confirm(
      t("Refuser dossier"),
      t("Voulez-vous vraiment refuser ce dossier double comptage")
    )

    if (!ok) return

    await rejectAgreement(entity.id, agreement.data.id)

    onResolve()
  }

  return (
    <Dialog wide onResolve={onResolve} className={styles.settingsPrompt}>
      <Box row>
        <DoubleCountingStatus status={dcaStatus} />
        <DialogTitle text={t("Dossier double comptage")} />
      </Box>

      <DialogText>
        <Trans>
          Pour le site de production <b>{{ productionSite }}</b> de{" "}
          <b>{{ producer }}</b>, soumis par <b>{{ user }}</b> le{" "}
          <b>{{ creationDate }}</b>
        </Trans>
      </DialogText>

      {!isReady && (
        <Alert level="warning" icon={AlertCircle} style={{ marginTop: 8 }}>
          <Trans>Dossier en attente de validation par la DGEC</Trans>
        </Alert>
      )}

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

      <div className={styles.modalTableContainer}>
        {focus === "aggregated_sourcing" && (
          <SourcingAggregationTable sourcing={agreement.data?.aggregated_sourcing ?? []} />
        )}

        {focus === "sourcing" && (
          <SourcingTable sourcing={agreement.data?.sourcing ?? []} />
        )}

        {focus === "production" && (
          <ProductionTable
            done={isDone}
            production={agreement.data?.production ?? []}
            entity={entity}
            quotas={quotas}
            setQuotas={setQuotas}
          />
        )}

        {focus === "status" && <StatusTable agreement={agreement.data} />}
      </div>

      <DialogButtons>
        <Box style={{ marginRight: "auto" }}>
          <a
            href={excelURL ?? "#"}
            target="_blank"
            rel="noreferrer"
            className={styles.settingsBottomLink}
          >
            <Upload />
            <Trans>Télécharger le dossier au format excel</Trans>
          </a>
          <a
            href={documentationURL ?? "#"}
            target="_blank"
            rel="noreferrer"
            className={styles.settingsBottomLink}
          >
            <Upload />
            <Trans>Télécharger la description de l'activité</Trans>
          </a>
        </Box>

        {!isDone && (
          <Fragment>
            {isAdmin && (
              <AsyncButton
                loading={approvingQuotas.loading}
                level="primary"
                icon={Save}
                onClick={submitQuotas}
              >
                <Trans>Enregistrer</Trans>
              </AsyncButton>
            )}

            <AsyncButton
              loading={approving.loading}
              disabled={!isReady || !hasQuotas}
              level="success"
              icon={Check}
              onClick={submitAccept}
            >
              <Trans>Accepter</Trans>
            </AsyncButton>
            <AsyncButton
              loading={rejecting.loading}
              disabled={!isReady}
              level="danger"
              icon={Cross}
              onClick={submitReject}
            >
              <Trans>Refuser</Trans>
            </AsyncButton>
          </Fragment>
        )}
        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Retour</Trans>
        </Button>
      </DialogButtons>

      {agreement.loading && <LoaderOverlay />}
    </Dialog>
  )
}
