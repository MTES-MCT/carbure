import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import Portal, { usePortal } from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { Trans, useTranslation } from "react-i18next"
import { Link, useLocation, useNavigate } from "react-router-dom"
import * as api from "../../api"
import {
  AgreementDetails,
  DoubleCountingStatus,
} from "../../../double-counting/types"
import AgreementStatusTag from "./agreement-status"
import { QuotasTable } from "../../../double-counting/components/quotas-table"
import { Fragment, useState } from "react"
import { compact } from "common/utils/collection"
import { SourcingFullTable } from "../../../double-counting/components/sourcing-table"
import { ProductionTable } from "../../../double-counting/components/production-table"
import { FilesTable } from "../../../double-counting/components/files-table"
import { Tabs } from "common/components/tabs2"
import { ROUTE_URLS } from "common/utils/routes"
import { ProductionSiteDetails } from "common/types"
import GenerateDecisionDialog from "../generate-decision-dialog/generate-decision-dialog"
import { ProductionSiteRecap } from "double-counting/components/applications/application-tabs/production-site-recap"

export const AgreementDetailsDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()

  const portal = usePortal()
  const match = useHashMatch("agreement/:id")

  const applicationResponse = useQuery(api.getDoubleCountingAgreement, {
    key: "dc-agreement",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const agreement: AgreementDetails | undefined =
    applicationResponse.result?.data

  const application = agreement?.application

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const openGenerateDecisionDialog = () => {
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
              <AgreementStatusTag status={agreement?.status} />
              {t("Agrément double comptage n°{{dcNumber}}", {
                dcNumber: agreement?.certificate_id || "FR_XXX_XXXX",
              })}
            </Dialog.Title>
            <Dialog.Description>
              <Trans
                values={{
                  producer: agreement?.producer ?? "N/A",
                  productionSite: agreement?.production_site ?? "N/A",
                }}
                components={{
                  Link: application ? (
                    <Link
                      to={ROUTE_URLS.ADMIN(entity.id).COMPANY_DETAIL(
                        application?.producer.id
                      )}
                      target="_blank"
                    />
                  ) : (
                    <Fragment />
                  ),
                }}
                defaults="Pour le site de production <b>{{ productionSite }}</b> de <b><Link>{{ producer }}</Link></b>"
              />
            </Dialog.Description>
          </>
        }
        footer={
          application && (
            <Button
              onClick={() => openGenerateDecisionDialog()}
              iconId="ri-download-line"
            >
              <Trans>Générer la décision</Trans>
            </Button>
          )
        }
      >
        {!application && !applicationResponse.loading && (
          <section>
            <p>
              <Trans>
                Aucune demande n'a été associée. Pour afficher les quotas
                approuvés, ajouter le demande associée à cet agrément dans
                l'onglet "demandes en attente".
              </Trans>
            </p>
          </section>
        )}
        {application &&
          application.status !== DoubleCountingStatus.ACCEPTED && (
            <section>
              <p>La demande est en cours de traitement...</p>
              <Button
                customPriority="link"
                asideY
                linkProps={{
                  to: `/org/${entity.id}/double-counting/applications#application/${application.id}`,
                }}
              >
                {"Voir la demande d'agrément à valider"}
              </Button>
            </section>
          )}

        {application &&
          application.status === DoubleCountingStatus.ACCEPTED && (
            <AgreementTabs
              agreement={agreement}
              productionSite={application.production_site}
            />
          )}

        {applicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

const AgreementTabs = ({
  agreement,
  productionSite,
}: {
  agreement: AgreementDetails
  productionSite: ProductionSiteDetails
}) => {
  const [focus, setFocus] = useState("production_site")
  const { t } = useTranslation()
  return (
    <>
      <Tabs
        sticky
        tabs={compact([
          {
            key: "production_site",
            label: t("Site de production"),
          },
          {
            key: "quotas",
            label: t("Quotas"),
          },
          {
            key: "sourcing_forecast",
            label: t("Approvisionnement"),
          },
          {
            key: "production",
            label: t("Production"),
          },
          {
            key: "fichiers",
            label: t("Fichiers"),
          },
        ])}
        focus={focus}
        onFocus={setFocus}
      />
      {focus === "production_site" && productionSite && (
        <ProductionSiteRecap productionSite={productionSite} />
      )}
      {focus === "quotas" && <QuotasTable quotas={agreement.quotas} />}

      {focus === "sourcing_forecast" && (
        <SourcingFullTable sourcing={agreement.application.sourcing ?? []} />
      )}

      {focus === "production" && (
        <ProductionTable
          production={agreement.application.production ?? []}
          sourcing={agreement.application.sourcing ?? []}
          hasAgreement={true}
        />
      )}
      {focus === "fichiers" && (
        <FilesTable application={agreement.application} />
      )}
    </>
  )
}
