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
import { AgreementDetails, DoubleCountingStatus as DCStatus, DoubleCountingApplicationDetails } from "../types"
import ApplicationStatus from "./application-status"
import ApplicationTabs from "./application-tabs"
import AgreementStatusTag from "./agreement-status"
import { ApplicationInfo } from "./application-info"


export const AgreementDetailsDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const match = useHashMatch("agreement/:id")

  const applicationResponse = useQuery(api.getDoubleCountingAgreement, {
    key: "dc-agreement",
    params: [entity.id, parseInt(match?.params.id!)]
  })



  const agreement: AgreementDetails | undefined = applicationResponse.result?.data.data

  const application = agreement?.application

  const applicationExcelURL =
    application &&
    `/api/v5/admin/double-counting/applications/details?dca_id=${application.id}&export=true`


  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog fullscreen onClose={closeDialog}>
        <header>
          <AgreementStatusTag status={agreement?.status} />
          <h1>{t("Agrément double comptage n°{{dcNumber}}", { dcNumber: agreement?.certificate_id || "FR_XXX_XXXX" })} </h1>
        </header>

        <main>

          <section>
            <p>
              <Trans
                values={{
                  producer: agreement?.producer ?? "N/A",
                  productionSite: agreement?.production_site ?? "N/A",
                }}
                defaults="Pour le site de production <b>{{ productionSite }}</b> de <b>{{ producer }}</b>"
              />
            </p>
          </section>

          {!application && !applicationResponse.loading && (
            <section>
              <p><Trans>Aucun dossier de demande n'a été associé.</Trans></p>
            </section>
          )}
          {application && <>
            <ApplicationTabs sourcing={application.sourcing} production={application.production} hasAgreement={true} />
          </>
          }
        </main>

        <footer>
          <Col style={{ gap: "var(--spacing-xs)", marginRight: "auto" }}>
            {application &&
              <DownloadLink
                href={applicationExcelURL ?? "#"}
                label={t("Télécharger le dossier au format excel")}
              />
            }
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

        {applicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}


