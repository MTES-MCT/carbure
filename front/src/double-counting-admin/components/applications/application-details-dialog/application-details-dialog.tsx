import useEntity from "common/hooks/entity"
import { EntityType } from "common/types"
import { Button } from "common/components/button2"
import { Confirm, Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import { useNotify } from "common/components/notifications"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useMutation, useQuery } from "common/hooks/async"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../../api"
import { DoubleCountingStatus as DCStatus } from "../../../../double-counting/types"
import { ApplicationInfo } from "../application-info"
import ApplicationStatus from "../../../../double-counting/components/application-status"
import ApplicationDetailsDialogValidateQuotas from "./application-details-dialog-validate-quotas"
import ApplicationDetailsDialogChangeStatus from "./application-details-dialog-change-status"
import GenerateDecisionDialog from "double-counting-admin/components/generate-decision-dialog/generate-decision-dialog"
import ApplicationTabs from "double-counting/components/applications/application-tabs"
import { Notice } from "common/components/notice"

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
    params: [entity.id, parseInt(match?.params.id || "")],

    onSuccess: (application) => {
      const applicationData = application.data
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

  const application = applicationResponse.result?.data
  const dcaStatus = application?.status ?? DCStatus.PENDING

  const hasQuotas = !application?.production.some(
    (p) => p.approved_quota === -1
  )

  const canWrite = entity.canWrite()

  const isPendingFiles =
    application?.has_dechets_industriels && application.documents.length <= 1

  const onUpdateQuotas = (quotas: Record<string, number>) => {
    setQuotasIsUpdated(true)
    setQuotas(quotas)
  }

  async function submitQuotas() {
    if (
      !application ||
      !entity ||
      ![EntityType.Administration, EntityType.ExternalAdmin].includes(
        entity.entity_type
      )
    ) {
      return
    }

    const updatedQuotas = Object.keys(quotas).map((id) => [
      parseInt(id),
      quotas[id]!,
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
        customVariant="danger"
        title={t("Refuser la demande d'agrément")}
        description={t("Voulez-vous vraiment refuser cette demande d'agrément double comptage ?")} // prettier-ignore
        confirm={t("Refuser")}
        icon="ri-close-line"
        onClose={close}
        onConfirm={async () => {
          if (application) {
            await rejectApplication.execute(entity.id, application.id)
          }
        }}
      />
    ))
  }

  async function submitChangeStatus() {
    if (!application) {
      return
    }

    portal((close) => (
      <ApplicationDetailsDialogChangeStatus
        application={application}
        onClose={close}
        onSuccess={() => {
          navigate({
            pathname: location.pathname,
          })
        }}
      />
    ))
  }

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const displayAcceptApplicationDetailsDialog = () => {
    if (!application) {
      return
    }

    portal((close) => (
      <ApplicationDetailsDialogValidateQuotas
        application={application}
        onClose={close}
        onValidate={() => {
          navigate({ search: location.search, hash: "#" })
        }}
      />
    ))
  }

  const displayGenerateDecisionDialog = () => {
    if (!application) {
      return
    }

    portal((close) => (
      <GenerateDecisionDialog application={application} onClose={close} />
    ))
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        fullscreen
        onClose={closeDialog}
        header={
          <>
            <Dialog.Title>
              <ApplicationStatus status={dcaStatus} />
              {t("Demande d'agrément double comptage")}
            </Dialog.Title>
            <Dialog.Description>
              <ApplicationInfo application={application} />

              {isPendingFiles && (
                <Notice
                  variant="info"
                  icon="ri-error-warning-line"
                  title={t("Spécificité Déchets industriels et CIVE:")}
                  style={{ marginTop: "var(--spacing-m)" }}
                >
                  {t("Fichier en attente")}
                </Notice>
              )}
            </Dialog.Description>
          </>
        }
        footer={
          canWrite &&
          !applicationResponse.loading && (
            <>
              <Button
                loading={rejectApplication.loading}
                disabled={applicationResponse.loading}
                priority="secondary"
                iconId="ri-close-line"
                onClick={submitChangeStatus}
              >
                <Trans>Changer le statut</Trans>
              </Button>
              <Button
                loading={rejectApplication.loading}
                disabled={applicationResponse.loading}
                customPriority="danger"
                iconId="ri-close-line"
                onClick={submitReject}
              >
                <Trans>Refuser</Trans>
              </Button>
              <Button
                disabled={applicationResponse.loading || !hasQuotas}
                customPriority="success"
                iconId="ri-check-line"
                onClick={displayAcceptApplicationDetailsDialog}
              >
                <Trans>Valider les quotas</Trans>
              </Button>

              <Button
                iconId="ri-download-line"
                priority="secondary"
                onClick={displayGenerateDecisionDialog}
                disabled={applicationResponse.loading || !hasQuotas}
              >
                <Trans>Générer la décision</Trans>
              </Button>
              <Button
                loading={approveQuotas.loading}
                disabled={!quotasIsUpdated}
                onClick={submitQuotas}
              >
                <Trans>Enregistrer</Trans>
              </Button>
            </>
          )
        }
      >
        {application && (
          <ApplicationTabs
            readOnly
            productionSite={application.production_site}
            sourcing={application.sourcing}
            production={application.production}
            quotas={quotas}
            setQuotas={onUpdateQuotas}
            files={application.documents}
            applicationId={application.id}
          />
        )}

        {applicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}
