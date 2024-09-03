import useEntity from "carbure/hooks/entity"
import { EntityType } from "carbure/types"
import { Button } from "common/components/button"
import { Alert } from "common/components/alert"
import { AlertTriangle } from "common/components/icons"
import { Confirm, Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Check, Cross, Download, Return, Save } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import { DoubleCountingStatus as DCStatus } from "../../../double-counting/types"
import { ApplicationInfo } from "./application-info"
import ApplicationStatus from "../../../double-counting/components/application-status"
import ApplicationTabs from "./application-tabs"
import { Input } from "common/components/input"
import ApplicationDetailsDialogAccept from "./application-details-dialog-accept"

export const ApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const [quotasIsUpdated, setQuotasIsUpdated] = useState(false)
  const [quotas, setQuotas] = useState<Record<string, number>>({})

  const [
    displayAcceptApplicationDetailsDialog,
    setDisplayAcceptApplicationDetailsDialog,
  ] = useState(false)
  const [industrialWastes, setIndustrialWastes] = useState("")
  const match = useHashMatch("application/:id")

  const applicationResponse = useQuery(api.getDoubleCountingApplication, {
    key: "dc-application",
    params: [entity.id, parseInt(match?.params.id || "")],

    onSuccess: (application) => {
      const applicationData = application.data.data
      if (applicationData === undefined) {
        setQuotas({})
        return
      }

      // automatically set the quotas to the asked value the first time the application is opened
      const quotas: Record<string, number> = {}
      applicationData.production.forEach((prod) => {
        quotas[prod.id] = prod.approved_quota >= 0 ? prod.approved_quota : 0
      })
      setQuotas(quotas)
    },
  })

  const approveQuotas = useMutation(api.approveDoubleCountingQuotas, {
    invalidates: ["dc-application", "dc-snapshot"],
    onSuccess: () => {
      setQuotasIsUpdated(false)
    },
  })

  const rejectApplication = useMutation(api.rejectDoubleCountingApplication, {
    invalidates: ["dc-applications", "dc-snapshot"],
    onSuccess: () => {
      navigate({
        pathname: location.pathname,
      })
      notify(t("La demande d'agrément a été refusé."), { variant: "success" })
    },
  })

  const application = applicationResponse.result?.data.data
  const dcaStatus = application?.status ?? DCStatus.Pending

  const isAdmin = entity?.entity_type === EntityType.Administration
  const hasQuotas = !application?.production.some(
    (p) => p.approved_quota === -1
  )

  const onUpdateQuotas = (quotas: Record<string, number>) => {
    setQuotasIsUpdated(true)
    setQuotas(quotas)
  }

  async function submitQuotas() {
    if (
      !application ||
      !entity ||
      entity?.entity_type !== EntityType.Administration
    ) {
      return
    }

    const updatedQuotas = Object.keys(quotas).map((id) => [
      parseInt(id),
      quotas[id],
    ])
    const done = await approveQuotas.execute(
      entity.id,
      application.id,
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

  async function submitReject() {
    portal((close) => (
      <Confirm
        variant="danger"
        title={t("Refuser la demande d'agrément")}
        description={t("Voulez-vous vraiment refuser cette demande d'agrément double comptage ?")} // prettier-ignore
        confirm={t("Refuser")}
        icon={Cross}
        onClose={close}
        onConfirm={async () => {
          if (application) {
            await rejectApplication.execute(entity.id, application.id)
          }
        }}
      />
    ))
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <>
      <Portal onClose={closeDialog}>
        <Dialog fullscreen onClose={closeDialog}>
          <header>
            <ApplicationStatus big status={dcaStatus} />
            <h1>{t("Demande d'agrément double comptage")} </h1>
          </header>

          <main>
            <ApplicationInfo application={application} />

            {application && (
              <ApplicationTabs
                productionSite={application.production_site}
                sourcing={application.sourcing}
                production={application.production}
                quotas={quotas}
                setQuotas={onUpdateQuotas}
              />
            )}
          </main>

          <footer>
            {/* {application &&
            <ApplicationDownloadButton application={application} />
          } */}
            {!applicationResponse.loading && (
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
                  disabled={applicationResponse.loading || !hasQuotas}
                  variant="success"
                  icon={Check}
                  action={() => setDisplayAcceptApplicationDetailsDialog(true)}
                >
                  <Trans>Valider les quotas</Trans>
                </Button>
                <Button
                  loading={rejectApplication.loading}
                  disabled={applicationResponse.loading}
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

          {applicationResponse.loading && <LoaderOverlay />}
        </Dialog>
      </Portal>
      <Portal>
        {displayAcceptApplicationDetailsDialog && (
          <ApplicationDetailsDialogAccept
            application={application}
            industrialWastes={industrialWastes}
            onChangeIndustrialWastes={setIndustrialWastes}
            onClose={() => setDisplayAcceptApplicationDetailsDialog(false)}
          />
        )}
      </Portal>
    </>
  )
}
