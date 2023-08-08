import useEntity from "carbure/hooks/entity"
import { EntityType } from "carbure/types"
import { Button } from "common/components/button"
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
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../api"
import { DoubleCountingStatus as DCStatus } from "../types"
import { ApplicationDownloadButton } from "./application-download-button"
import { ApplicationInfo } from "./application-info"
import ApplicationStatus from "./application-status"
import ApplicationTabs from "./application-tabs"


export const ApplicationDetailsDialog = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const portal = usePortal()
  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const [quotasIsUpdated, setQuotasIsUpdated] = useState(false)
  const [quotas, setQuotas] = useState<Record<string, number>>({})
  const match = useHashMatch("application/:id")


  const applicationResponse = useQuery(api.getDoubleCountingApplication, {
    key: "dc-application",
    params: [entity.id, parseInt(match?.params.id!)],

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

    const updatedQuotas = Object.keys(quotas).map((id) => [parseInt(id), quotas[id]])
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
          if (application) {
            await approveApplication.execute(entity.id, application.id)
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
    <Portal onClose={closeDialog}>
      <Dialog fullscreen onClose={closeDialog}>
        <header>
          <ApplicationStatus big status={dcaStatus} />
          <h1>{t("Dossier double comptage")} </h1>
        </header>

        <main>

          <ApplicationInfo application={application} />

          <ApplicationTabs sourcing={application?.sourcing} production={application?.production} quotas={quotas} setQuotas={onUpdateQuotas} />

        </main>

        <footer>
          {application &&
            <ApplicationDownloadButton application={application} />
          }
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
                action={submitAccept}
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
  )
}

