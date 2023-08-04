import useEntity from "carbure/hooks/entity"
import { EntityType } from "carbure/types"
import { Button, DownloadLink } from "common/components/button"
import { Confirm, Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import {
  Check,
  Cross,
  Return,
  Save
} from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { Col, LoaderOverlay } from "common/components/scaffold"
import Tabs from "common/components/tabs"
import { useMutation, useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../api"
import { DoubleCountingStatus as DCStatus, DoubleCountingProduction, DoubleCountingSourcing } from "../types"
import DoubleCountingStatus from "./dc-status"
import {
  ProductionTable,
  SourcingFullTable
} from "./dc-tables"


export const DoubleCountingApplicationDialog = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const [quotasIsUpdated, setQuotasIsUpdated] = useState(false)
  const [quotas, setQuotas] = useState<Record<string, number>>({})
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
    invalidates: ["dc-applications", "dc-snapshot"],
    onSuccess: () => {
      setQuotasIsUpdated(false)
    }
  })

  const approveApplication = useMutation(api.approveDoubleCountingApplication, {
    invalidates: ["dc-applications", "dc-snapshot", "dc-agreements"],
    onSuccess: () => {
      navigate("/org/9/double-counting/agreements")
      notify(t("Le dossier a été accepté."), { variant: "success" })
    }
  })

  const rejectApplication = useMutation(api.rejectDoubleCountingApplication, {
    invalidates: ["dc-applications", "dc-snapshot"],
    onSuccess: () => {
      navigate({
        pathname: location.pathname,
      })
      notify(t("Le dossier a été refusé."), { variant: "success" })
    }
  })


  const applicationData = application.result?.data.data
  const dcaStatus = applicationData?.status ?? DCStatus.Pending


  const isAdmin = entity?.entity_type === EntityType.Administration
  const hasQuotas = !applicationData?.production.some(
    (p) => p.approved_quota === -1
  )


  const productionSite = applicationData?.production_site ?? "N/A"
  const producer = applicationData?.producer.name ?? "N/A"
  const user = applicationData?.producer_user ?? "N/A"
  const creationDate = applicationData?.created_at
    ? formatDate(applicationData.created_at)
    : "N/A"

  const excelURL =
    applicationData &&
    `/api/v5/admin/double-counting/applications/details?dca_id=${applicationData.id}&export=true`

  const onUpdateQuotas = (quotas: Record<string, number>) => {
    setQuotasIsUpdated(true)
    setQuotas(quotas)
  }

  async function submitQuotas() {
    if (
      !applicationData ||
      !entity ||
      entity?.entity_type !== EntityType.Administration
    ) {
      return
    }

    const updatedQuotas = Object.keys(quotas).map((id) => [parseInt(id), quotas[id]])
    const done = await approveQuotas.execute(
      entity.id,
      applicationData.id,
      updatedQuotas
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
        description={t("Voulez-vous vraiment accepter ce dossier double comptage ? Une fois accepté, vous retrouverez l’agrément correspondant dans la liste des agréments actifs.")} // prettier-ignore
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

          <ApplicationDetails sourcing={applicationData?.sourcing} production={applicationData?.production} quotas={quotas} setQuotas={onUpdateQuotas} />

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
                  disabled={!quotasIsUpdated}
                  variant="primary"
                  icon={Save}
                  action={submitQuotas}
                >
                  <Trans>Enregistrer</Trans>
                </Button>
              )}

              <Button
                loading={approveQuotas.loading}
                disabled={application.loading || !hasQuotas}


                variant="success"
                icon={Check}
                action={submitAccept}
              >
                <Trans>Valider les quotas</Trans>
              </Button>
              <Button
                loading={rejectApplication.loading}
                disabled={application.loading}
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