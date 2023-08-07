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
import { useMutation, useQuery } from "common/hooks/async"
import { formatDate } from "common/utils/formatters"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../api"
import { DoubleCountingStatus as DCStatus } from "../types"
import ApplicationStatus from "./application-status"
import ApplicationTabs from "./application-tabs"


export const AgreementDetailsDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const match = useHashMatch("agreement/:id")

  const application = useQuery(api.getDoubleCountingAgreement, {
    key: "dc-agreement",
    params: [entity.id, parseInt(match?.params.id!)]
  })



  const applicationData = application.result?.data.data
  console.log('applicationData:', applicationData)
  const dcaStatus = applicationData?.status ?? DCStatus.Pending


  const excelURL =
    applicationData &&
    `/api/v5/admin/double-counting/applications/details?dca_id=${applicationData.id}&export=true`


  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog fullscreen onClose={closeDialog}>
        <header>
          <ApplicationStatus big status={dcaStatus} />
          <h1>{t("Agrément double comptage")} </h1>
        </header>
        {/* 
        <main>

          <section>
            <p>
              <Trans
                values={{ producer, productionSite, creationDate, user }}
                defaults="Pour le site de production <b>{{ productionSite }}</b> de <b>{{ producer }}</b>, soumis par <b>{{ user }}</b> le <b>{{ creationDate }}</b>"
              />
            </p>
          </section>

          <ApplicationTabs sourcing={applicationData?.sourcing} production={applicationData?.production} quotas={quotas} setQuotas={onUpdateQuotas} />

        </main> */}

        <footer>
          <Col style={{ gap: "var(--spacing-xs)", marginRight: "auto" }}>
            <DownloadLink
              href={excelURL ?? "#"}
              label={t("Télécharger le dossier au format excel")}
            />
          </Col>


          {/* {!application.loading && (
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
          )} */}
          <Button icon={Return} action={closeDialog}>
            <Trans>Retour</Trans>
          </Button>
        </footer>

        {application.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}


