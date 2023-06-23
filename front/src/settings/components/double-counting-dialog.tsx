import { Entity } from "carbure/types"
import Button, { DownloadLink, MailTo } from "common/components/button"
import Dialog, { Confirm } from "common/components/dialog"
import { Cross, Plus, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import { Col, LoaderOverlay } from "common/components/scaffold"
import { actionColumn, Cell } from "common/components/table"
import Tabs from "common/components/tabs"
import { useMutation, useQuery } from "common/hooks/async"
import { compact } from "common/utils/collection"
import { formatDate, formatNumber } from "common/utils/formatters"
import DoubleCountingStatus from "double-counting/components/dc-status"
import { SourcingAggregationTable } from "double-counting/components/dc-tables"
import YearTable from "double-counting/components/year-table"
import {
  DoubleCountingProduction,
  DoubleCountingSourcing,
  DoubleCountingStatus as DCStatus,
} from "double-counting/types"
import { Fragment, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/double-counting"
import DoubleCountingProductionDialog from "./double-counting-production-dialog"
import QuotasTable from "./double-counting-quotas-dialog"
import DoubleCountingSourcingDialog from "./double-counting-sourcing-dialog"

type DoubleCountingDialogProps = {
  entity: Entity
  agreementID: number
  onClose: () => void
}

const DoubleCountingDialog = ({
  entity,
  agreementID,
  onClose,
}: DoubleCountingDialogProps) => {
  const { t } = useTranslation()
  const entityID = entity?.id
  const portal = usePortal()

  const [focus, setFocus] = useState("aggregated_sourcing")

  const agreement = useQuery(api.getDoubleCountingDetails, {
    key: "dc-details",
    params: [entityID, agreementID],
  })

  const deleteSourcing = useMutation(api.deleteDoubleCountingSourcing, {
    invalidates: ["dc-details"],
  })

  const deleteProduction = useMutation(api.deleteDoubleCountingProduction, {
    invalidates: ["dc-details"],
  })

  const dcaID = agreement.result?.data.data?.id ?? -1
  const dcaStatus = agreement.result?.data.data?.status ?? DCStatus.Pending

  const isAccepted = dcaStatus === DCStatus.Accepted
  const isFinal = dcaStatus !== DCStatus.Pending

  const sourcingRows: DoubleCountingSourcing[] =
    agreement.result?.data.data?.sourcing ?? []

  const agreementData = agreement.result?.data.data
  const productionRows = agreementData?.production ?? []

  const productionSite = agreementData?.production_site ?? "N/A"
  const creationDate = agreementData?.creation_date
    ? formatDate(agreementData.creation_date)
    : "N/A"

  const documentationFile = agreementData?.documents.find(
    (doc) => doc.file_type === "SOURCING"
  )
  const decisionFile = agreementData?.documents.find(
    (doc) => doc.file_type === "DECISION"
  )

  const excelURL =
    agreementData &&
    `/api/v3/doublecount/agreement?dca_id=${dcaID}&entity_id=${entity?.id}&export=true`
  const documentationURL =
    entity &&
    documentationFile &&
    `/api/v3/doublecount/download-documentation?entity_id=${entity.id}&dca_id=${dcaID}&file_id=${documentationFile.id}`
  const decisionURL =
    entity &&
    decisionFile &&
    `/api/v3/doublecount/download-admin-decision?entity_id=${entity.id}&dca_id=${dcaID}&file_id=${decisionFile.id}`

  function showSourcingDialog(sourcing: DoubleCountingSourcing) {
    if (isFinal) return

    portal((close) => (
      <DoubleCountingSourcingDialog
        entity={entity}
        dcaID={dcaID}
        sourcing={sourcing}
        onClose={close}
      />
    ))
  }

  function showNewSourcingDialog() {
    if (isFinal) return

    portal((close) => (
      <DoubleCountingSourcingDialog
        add
        entity={entity}
        dcaID={dcaID}
        onClose={close}
      />
    ))
  }

  async function removeSourcingRow(sourcingID: number) {
    if (!entity || isFinal) return

    portal((close) => (
      <Confirm
        variant="danger"
        title={t("Supprimer approvisionnement")}
        description={t("Voulez-vous supprimer cette ligne d'approvisionnement ?")} // prettier-ignore
        confirm="Supprimer"
        icon={Cross}
        onConfirm={() => deleteSourcing.execute(entity.id, sourcingID)}
        onClose={close}
      />
    ))
  }

  function showProductionDialog(production: DoubleCountingProduction) {
    if (isFinal) return

    portal((close) => (
      <DoubleCountingProductionDialog
        entity={entity}
        dcaID={dcaID}
        production={production}
        onClose={close}
      />
    ))
  }

  function showNewProductionDialog() {
    if (isFinal) return

    portal((close) => (
      <DoubleCountingProductionDialog
        add
        entity={entity}
        dcaID={dcaID}
        onClose={close}
      />
    ))
  }

  async function removeProductionRow(productionID: number) {
    if (!entity || isFinal) return

    portal((close) => (
      <Confirm
        variant="danger"
        title={t("Supprimer production")}
        description={t("Voulez-vous supprimer cette ligne de production ?")} // prettier-ignore
        confirm="Supprimer"
        icon={Cross}
        onConfirm={() => deleteProduction.execute(entity.id, productionID)}
        onClose={close}
      />
    ))
  }

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <DoubleCountingStatus big status={dcaStatus} />
        <h1>{t("Dossier double comptage")}</h1>
      </header>

      <main>
        <section>
          <p>
            <Trans
              values={{ productionSite, creationDate }}
              defaults="Pour le site de production <b>{{ productionSite }}</b>, soumis le <b>{{ creationDate }}</b>"
            />
          </p>

          <p>
            <Trans>
              Pour toute question concernant l'évolution de votre dossier,
              contactez-nous à l'adresse{" "}
              <MailTo user="carbure" host="beta.gouv.fr">
                disponible sur ce lien
              </MailTo>
            </Trans>
          </p>
        </section>

        <section>
          <Tabs
            tabs={compact([
              { key: "aggregated_sourcing", label: t("Approvisionnement") },
              { key: "sourcing", label: t("Approvisionnement (détaillé)") },
              { key: "production", label: t("Production") },
              isAccepted && { key: "quotas", label: t("Suivi des quotas") },
            ])}
            focus={focus}
            onFocus={setFocus}
          />
        </section>

        {focus === "aggregated_sourcing" && (
          <SourcingAggregationTable
            sourcing={agreementData?.aggregated_sourcing ?? []}
          />
        )}

        {focus === "sourcing" && (
          <Fragment>
            <YearTable<DoubleCountingSourcing>
              rows={sourcingRows}
              onAction={showSourcingDialog}
              columns={compact([
                {
                  header: t("Matière première"),
                  cell: (s) => (
                    <Cell text={t(s.feedstock.code, { ns: "feedstocks" })} />
                  ),
                },
                {
                  header: t("Poids en tonnes"),
                  cell: (s) => <Cell text={formatNumber(s.metric_tonnes)} />,
                },
                {
                  header: t("Origine"),
                  cell: (s) => (
                    <Cell
                      text={t(s.origin_country.code_pays, { ns: "countries" })}
                    />
                  ),
                },
                {
                  header: t("Approvisionnement"),
                  cell: (s) =>
                    s.supply_country && (
                      <Cell
                        text={t(s.supply_country.code_pays, {
                          ns: "countries",
                        })}
                      />
                    ),
                },
                {
                  header: t("Transit"),
                  cell: (s) =>
                    s.transit_country && (
                      <Cell
                        text={t(s.transit_country.code_pays, {
                          ns: "countries",
                        })}
                      />
                    ),
                },
                !isFinal &&
                actionColumn((s) => [
                  <Button
                    captive
                    variant="icon"
                    icon={Cross}
                    action={() => removeSourcingRow(s.id)}
                    title={t("Supprimer approvisionnement")}
                  />,
                ]),
              ])}
            />

            {!isFinal && (
              <section>
                <Button
                  variant="link"
                  icon={Plus}
                  action={showNewSourcingDialog}
                  label={t("Ajouter une ligne d'approvisionnement")}
                />
              </section>
            )}
          </Fragment>
        )}

        {focus === "production" && (
          <Fragment>
            <YearTable<DoubleCountingProduction>
              rows={productionRows}
              onAction={showProductionDialog}
              columns={compact([
                {
                  header: t("Matière première"),
                  cell: (p) => (
                    <Cell text={t(p.feedstock.code, { ns: "feedstocks" })} />
                  ),
                },
                {
                  header: t("Biocarburant"),
                  cell: (p) => (
                    <Cell text={t(p.biofuel.code, { ns: "biofuels" })} />
                  ),
                },
                {
                  header: t("Prod. max"),
                  cell: (p) => (
                    <Cell text={formatNumber(p.max_production_capacity ?? 0)} />
                  ),
                },
                {
                  header: t("Prod. estimée"),
                  cell: (p) => (
                    <Cell text={formatNumber(p.estimated_production)} />
                  ),
                },
                {
                  header: t("Quota demandé"),
                  cell: (p) => <Cell text={formatNumber(p.requested_quota)} />,
                },
                {
                  header: t("Quota approuvé"),
                  cell: (p) =>
                    p.approved_quota === -1 ? (
                      t("En attente")
                    ) : (
                      <Cell text={formatNumber(p.approved_quota)} />
                    ),
                },
                !isFinal &&
                actionColumn((s) => [
                  <Button
                    captive
                    variant="icon"
                    icon={Cross}
                    action={() => removeProductionRow(s.id)}
                    title={t("Supprimer production")}
                  />,
                ]),
              ])}
            />

            {!isFinal && (
              <section>
                <Button
                  variant="link"
                  icon={Plus}
                  action={showNewProductionDialog}
                  label={t("Ajouter une ligne de production")}
                />
              </section>
            )}
          </Fragment>
        )}

        {focus === "quotas" && (
          <QuotasTable entity={entity} agreement={agreementData} />
        )}
      </main>
      <footer>
        <Col style={{ gap: "var(--spacing-xs)", marginRight: "auto" }}>
          <DownloadLink
            href={excelURL ?? "#"}
            label={t("Télécharger le dossier au format excel")}
          />
          <DownloadLink
            href={documentationURL ?? "#"}
            label={t("Télécharger la description de l'activité")}
          />
          {decisionURL && (
            <DownloadLink
              href={decisionURL ?? "#"}
              label={t("Télécharger la décision de l'administration")}
            />
          )}
        </Col>

        <Button icon={Return} action={onClose}>
          <Trans>Retour</Trans>
        </Button>
      </footer>

      {agreement.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default DoubleCountingDialog
