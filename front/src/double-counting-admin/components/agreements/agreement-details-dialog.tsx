import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { useHashMatch } from "common/components/hash-route"
import { Return } from "common/components/icons"
import Portal from "common/components/portal"
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
import Tabs from "common/components/tabs"
import { ROUTE_URLS } from "common/utils/routes"
import { ProductionSiteForm } from "settings/components/production-site-dialog"
import { ProductionSiteDetails } from "carbure/types"

export const AgreementDetailsDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const match = useHashMatch("agreement/:id")

  const applicationResponse = useQuery(api.getDoubleCountingAgreement, {
    key: "dc-agreement",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const agreement: AgreementDetails | undefined =
    applicationResponse.result?.data.data

  const application = agreement?.application

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog fullscreen onClose={closeDialog}>
        <header>
          <AgreementStatusTag status={agreement?.status} />
          <h1>
            {t("Agrément double comptage n°{{dcNumber}}", {
              dcNumber: agreement?.certificate_id || "FR_XXX_XXXX",
            })}{" "}
          </h1>
        </header>

        <main>
          <section>
            <p>
              <Trans
                values={{
                  producer: agreement?.producer ?? "N/A",
                  productionSite: agreement?.production_site ?? "N/A",
                }}
                components={{
                  Link: application ? (
                    <Link
                      to={ROUTE_URLS.ADMIN_COMPANY_DETAIL(
                        entity.id,
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
            </p>
          </section>

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
            application.status !== DoubleCountingStatus.Accepted && (
              <section>
                <p>La demande est en cours de traitement...</p>
                <Button
                  variant="link"
                  asideY
                  action={() =>
                    navigate(
                      `/org/${entity.id}/double-counting/applications#application/${application.id}`
                    )
                  }
                >
                  {"Voir la demande d'agrément à valider"}
                </Button>
              </section>
            )}

          {application &&
            application.status === DoubleCountingStatus.Accepted && (
              <AgreementTabs
                agreement={agreement}
                productionSite={application.production_site}
              />
            )}
        </main>

        <footer>
          {/* {application &&
            <ApplicationDownloadButton application={application} />
          } */}

          <Button icon={Return} action={closeDialog}>
            <Trans>Retour</Trans>
          </Button>
        </footer>

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
      <section>
        <Tabs
          variant="switcher"
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
          ])}
          focus={focus}
          onFocus={setFocus}
        />
      </section>
      {focus === "production_site" && productionSite && (
        <section>
          <ProductionSiteForm readOnly productionSite={productionSite} />
        </section>
      )}
      {focus === "quotas" && (
        <section>
          <QuotasTable quotas={agreement.quotas} />
        </section>
      )}

      {focus === "sourcing_forecast" && (
        <section>
          <SourcingFullTable sourcing={agreement.application.sourcing ?? []} />
        </section>
      )}

      {focus === "production" && (
        <section>
          <ProductionTable
            production={agreement.application.production ?? []}
            sourcing={agreement.application.sourcing ?? []}
            hasAgreement={true}
          />
        </section>
      )}
    </>
  )
}
