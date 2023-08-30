import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import {
  Return
} from "common/components/icons"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import { AgreementDetails, DoubleCountingStatus } from "../../types"
import AgreementStatusTag from "./agreement-status"
import { ApplicationDownloadButton } from "../applications/application-download-button"
import ApplicationTabs from "../applications/application-tabs"


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
              <p><Trans>Aucun dossier de demande n'a été associé. Pour afficher les quotas approuvés, ajouter le dossier associé à cet agrément dans l'onglet "dossiers en attente".</Trans></p>
            </section>
          )}
          {application && application.status != DoubleCountingStatus.Accepted &&
            <section>
              <p>Le dossier est en cours de validation...</p>
              <Button
                variant="link"

                asideY
                action={() => navigate(`/org/${entity.id}/double-counting/applications#application/${application.id}`)}>
                {("Voir le dossier à valider")}

              </Button>

            </section>
          }
          {application && application.status === DoubleCountingStatus.Accepted && <>
            <ApplicationTabs sourcing={application.sourcing} production={application.production} hasAgreement={true} />
          </>
          }
        </main>

        <footer>
          {application &&
            <ApplicationDownloadButton application={application} />
          }

          <Button icon={Return} action={closeDialog}>
            <Trans>Retour</Trans>
          </Button>
        </footer>

        {applicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal >
  )
}

