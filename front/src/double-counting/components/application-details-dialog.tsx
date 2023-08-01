import { Fragment, useState } from "react"
import { useTranslation, Trans } from "react-i18next"
import { Admin, DoubleCountingStatus as DCStatus, DoubleCountingProduction, DoubleCountingSourcing } from "../types"
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
  SourcingFullTable,
} from "./dc-tables"
import { FileInput } from "common/components/input"
import { useMutation, useQuery } from "common/hooks/async"
import Portal, { usePortal } from "common/components/portal"
import { formatDate } from "common/utils/formatters"
import useEntity from "carbure/hooks/entity"
import { useHashMatch } from "common/components/hash-route"
import { useLocation, useNavigate } from "react-router-dom"


export const DoubleCountingApplicationDialog = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const [focus, setFocus] = useState("aggregated_sourcing")
  const [quotas, setQuotas] = useState<Record<string, number>>({})
  console.log('quotas:', quotas)
  const match = useHashMatch("application/:id")


  const application = useQuery(api.getDoubleCountingApplication, {
    key: "dc-application",
    params: [parseInt(match?.params.id!)],

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
          prod.approved_quota >= 0 ? prod.approved_quota : 0
      })
      setQuotas(quotas)
    },
  })

  const approveQuotas = useMutation(api.approveDoubleCountingQuotas, {
    invalidates: ["dc-application", "dc-snapshot"],
  })

  const approveApplication = useMutation(api.approveDoubleCountingApplication, {
    invalidates: ["dc-application", "dc-snapshot"],
  })

  const rejectApplication = useMutation(api.rejectDoubleCountingApplication, {
    invalidates: ["dc-application", "dc-snapshot"],
  })


  const applicationData = application.result?.data.data
  console.log('applicationData:', applicationData)
  const dcaStatus = applicationData?.status ?? DCStatus.Pending


  const isAdmin = entity?.entity_type === EntityType.Administration
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


  const excelURL =
    applicationData &&
    `/api/v5/admin/double-counting/applications/details?dca_id=${applicationData.id}&export=true`

  async function submitQuotas() {
    if (
      !applicationData ||
      !entity ||
      entity?.entity_type !== EntityType.Administration
    ) {
      return
    }

    const done = await approveQuotas.execute(
      entity.id,
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

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog fullscreen onClose={closeDialog}>
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

          <ApplicationDetails sourcing={applicationData?.sourcing} production={applicationData?.production} quotas={quotas} setQuotas={setQuotas} />

        </main>

        <footer>
          <Col style={{ gap: "var(--spacing-xs)", marginRight: "auto" }}>
            <DownloadLink
              href={excelURL ?? "#"}
              label={t("Télécharger le dossier au format excel")}
            />
          </Col>


          {!application.loading && (
            <>
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
                <Trans>Valider les quotas</Trans>
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
            </>
          )}
          <Button icon={Return} action={closeDialog}>
            <Trans>Retour</Trans>
          </Button>
        </footer>

        {application.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}



interface ApplicationDetailsProps {
  production?: DoubleCountingProduction[]
  sourcing?: DoubleCountingSourcing[]
  quotas?: Record<string, number>
  setQuotas?: (quotas: Record<string, number>) => void
}

const ApplicationDetails = ({ production, sourcing, quotas, setQuotas }: ApplicationDetailsProps) => {
  const [focus, setFocus] = useState("production")
  const { t } = useTranslation()

  return <>
    <section>
      <Tabs
        variant="switcher"
        tabs={[
          {
            key: "sourcing_forecast",
            label: t("Approvisionnement"),
          },
          {
            key: "production",
            label: t("Production"),
          }

        ]}
        focus={focus}
        onFocus={setFocus}
      />

    </section>

    {focus === "sourcing_forecast" &&
      <section>
        <SourcingFullTable
          sourcing={sourcing ?? []}
        />
      </section>
    }


    {focus === "production" &&
      <section>
        <ProductionTable
          production={production ?? []}
          quotas={quotas ?? {}}
          setQuotas={setQuotas}
        />
      </section>
    }
  </>
}