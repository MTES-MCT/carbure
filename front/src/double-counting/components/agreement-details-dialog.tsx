import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { useHashMatch } from "common/components/hash-route"
import Portal from "common/components/portal"
import { LoaderOverlay } from "common/components/scaffold"
import { Tabs } from "common/components/tabs2"
import { useQuery } from "common/hooks/async"
import { compact } from "common/utils/collection"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "../api"
import AgreementStatusTag from "../../double-counting-admin/components/agreements/agreement-status"
import { ProductionTable } from "./production-table"
import { QuotasTable } from "./quotas-table"
import { SourcingFullTable } from "./sourcing-table"
import { AgreementDetails, DoubleCountingStatus } from "../types"
import {
  BuildingFill,
  BuildingLine,
  ProfileFill,
  ProfileLine,
  UserFill,
  UserLine,
} from "common/components/icon"

export const AgreementDetailsDialog = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()
  const match = useHashMatch("double-counting/agreements/:id")

  const applicationResponse = useQuery(api.getDoubleCountingAgreementDetails, {
    key: "dc-agreement",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const agreement = applicationResponse.result?.data

  const application = agreement?.application

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        fullscreen
        onClose={closeDialog}
        gap="lg"
        header={
          <>
            <Dialog.Title style={{ justifyContent: "space-between" }}>
              {t("Agrément double comptage n°{{dcNumber}}", {
                dcNumber: agreement?.certificate_id || "FR_XXX_XXXX",
              })}
              <AgreementStatusTag status={agreement?.status} />
            </Dialog.Title>
            <Dialog.Description>
              <Trans
                values={{
                  producer: agreement?.producer ?? "N/A",
                  productionSite: agreement?.production_site ?? "N/A",
                }}
                defaults="Pour le site de production <b>{{ productionSite }}</b> de <b>{{ producer }}</b>"
              />
            </Dialog.Description>
          </>
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
                onClick={() =>
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
          application.status === DoubleCountingStatus.ACCEPTED && (
            <AgreementTabs agreement={agreement} />
          )}

        {applicationResponse.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

const AgreementTabs = ({ agreement }: { agreement: AgreementDetails }) => {
  const [focus, setFocus] = useState("quotas")
  const { t } = useTranslation()

  return (
    <>
      <Tabs
        tabs={compact([
          {
            key: "quotas",
            label: t("Quotas"),
            icon: BuildingLine,
            iconActive: BuildingFill,
          },
          {
            key: "sourcing_forecast",
            label: t("Approvisionnement"),
            icon: ProfileLine,
            iconActive: ProfileFill,
          },
          {
            key: "production",
            label: t("Production"),
            icon: UserLine,
            iconActive: UserFill,
          },
        ])}
        focus={focus}
        onFocus={setFocus}
        sticky
      />
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
    </>
  )
}
