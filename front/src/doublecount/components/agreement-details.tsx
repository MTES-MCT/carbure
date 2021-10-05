import { Fragment, useState, useEffect } from "react"
import { useTranslation, Trans } from "react-i18next"
import {
  DoubleCountingStatus,
  DoubleCountingSourcing,
  DoubleCountingProduction,
  EntityType,
  DoubleCountingDetails,
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
import { DCStatus } from "settings/components/double-counting"
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

export enum Admin {
  DGEC = "MTE - DGEC",
  DGDDI = "DGDDI",
  DGPE = "DGPE",
}

type ValidationStatus = {
  approved: boolean
  date: string
  user: string
  entity: string
}

type SourcingTableProps = {
  sourcing: DoubleCountingSourcing[]
}

const SourcingTable = ({ sourcing }: SourcingTableProps) => {
  const { t } = useTranslation()

  const columns: Column<DoubleCountingSourcing>[] = [
    padding,
    {
      header: t("Matière première"),
      render: (s) => t(s.feedstock.code, { ns: "feedstocks" }),
    },
    {
      header: t("Poids en tonnes"),
      render: (s) => s.metric_tonnes,
    },
    {
      header: t("Origine"),
      render: (s) => t(s.origin_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Approvisionnement"),
      render: (s) =>
        s.supply_country && t(s.supply_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Transit"),
      render: (s) =>
        s.transit_country &&
        t(s.transit_country.code_pays, { ns: "countries" }),
    },
    padding,
  ]

  const rows = sourcing.map((v) => ({ value: v }))

  return <YearTable columns={columns} rows={rows} />
}

type ProductionTableProps = {
  done?: boolean
  entity: EntitySelection
  quotas: Record<string, string>
  production: DoubleCountingProduction[]
  setQuotas: (quotas: Record<string, string>) => void
}

const ProductionTable = ({
  done,
  entity,
  quotas,
  production,
  setQuotas,
}: ProductionTableProps) => {
  const { t } = useTranslation()

  const productionColumns: Column<DoubleCountingProduction>[] = [
    padding,
    {
      header: t("Matière première"),
      render: (p) => t(p.feedstock.code, { ns: "feedstocks" }),
    },
    {
      header: t("Biocarburant"),
      render: (p) => t(p.biofuel.code, { ns: "biofuels" }),
    },
    {
      header: t("Prod. max"),
      render: (p) => p.max_production_capacity,
    },
    {
      header: t("Prod. estimée"),
      render: (p) => p.estimated_production,
    },
    {
      header: t("Quota demandé"),
      render: (p) => p.requested_quota,
    },
    {
      header: t("Quota approuvé"),
      render: (p) => {
        if (done || entity?.entity_type !== EntityType.Administration) {
          return p.approved_quota >= 0 ? p.approved_quota : p.requested_quota
        }

        return (
          <Input
            value={quotas[p.id]}
            onChange={(e) =>
              setQuotas({
                ...quotas,
                [p.id]: e.target.value,
              })
            }
          />
        )
      },
    },
    padding,
  ]

  const rows = production.map((v) => ({ value: v }))

  return <YearTable columns={productionColumns} rows={rows} />
}

type StatusTableProps = {
  agreement: DoubleCountingDetails | null
}

const StatusTable = ({ agreement }: StatusTableProps) => {
  const { t } = useTranslation()

  const statusColumns: Column<ValidationStatus>[] = [
    padding,
    {
      header: t("Administration"),
      render: (s) => s.entity,
    },
    {
      header: t("Statut"),
      render: (s) =>
        !s.approved && s.user
          ? t("Refusé")
          : s.approved
          ? t("Accepté")
          : t("En attente"),
    },
    {
      header: t("Validateur"),
      render: (s) => s.user || "N/A",
    },
    {
      header: t("Date"),
      render: (s) => formatDate(s.date),
    },
    padding,
  ]

  const statusRows: Row<ValidationStatus>[] = [
    {
      approved: agreement?.dgec_validated ?? false,
      date: agreement?.dgec_validated_dt ?? "",
      user: agreement?.dgec_validator ?? "",
      entity: Admin.DGEC,
    },
    {
      approved: agreement?.dgddi_validated ?? false,
      date: agreement?.dgddi_validated_dt ?? "",
      user: agreement?.dgddi_validator ?? "",
      entity: Admin.DGDDI,
    },
    {
      approved: agreement?.dgpe_validated ?? false,
      date: agreement?.dgpe_validated_dt ?? "",
      user: agreement?.dgpe_validator ?? "",
      entity: Admin.DGPE,
    },
  ].map((value) => ({ value }))

  return <Table columns={statusColumns} rows={statusRows} />
}

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

  const [focus, setFocus] = useState("sourcing")
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

  const dcaStatus = agreement.data?.status ?? DoubleCountingStatus.Pending

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
    approved || agreement.data?.status === DoubleCountingStatus.Rejected
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
        <DCStatus status={dcaStatus} />
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
        <Alert level="warning" icon={AlertCircle}>
          <Trans>Dossier en attente de validation par la DGEC</Trans>
        </Alert>
      )}

      <Tabs
        tabs={[
          { key: "sourcing", label: t("Approvisionnement") },
          { key: "production", label: t("Production") },
          { key: "status", label: t("Statut") },
        ]}
        focus={focus}
        onFocus={setFocus}
      />

      <div className={styles.modalTableContainer}>
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
              disabled={!isReady}
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
