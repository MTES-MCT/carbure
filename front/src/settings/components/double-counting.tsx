import { Fragment, useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { Entity, UserRole, ProductionSite } from "carbure/types"
import {
  DoubleCounting,
  DoubleCountingStatus as DCStatus,
  DoubleCountingSourcing,
  DoubleCountingProduction,
  QuotaDetails,
} from "doublecount/types"
import { Col, LoaderOverlay } from "common/components/scaffold"
import { useRights } from "carbure/hooks/entity"
import Table, { Cell, actionColumn, Column } from "common/components/table"
import Button, { DownloadLink, MailTo } from "common/components/button"
import {
  AlertCircle,
  Check,
  Cross,
  Plus,
  Return,
  Save,
  Upload,
} from "common/components/icons"
import { Alert } from "common/components/alert"
import Dialog, { Confirm } from "common/components/dialog"
import {
  findBiofuels,
  findCountries,
  findFeedstocks,
  findProductionSites,
} from "carbure/api"
import AutoComplete from "common/components/autocomplete"
import * as api from "../api/double-counting"
import { useMutation, useQuery } from "common/hooks/async"
import Tabs from "common/components/tabs"
import { Form } from "common/components/form"
import { NumberInput } from "common/components/input"
import { useForm } from "common/components/form"
import YearTable from "doublecount/components/year-table"
import DoubleCountingStatus from "doublecount/components/dc-status"
import { SourcingAggregationTable } from "doublecount/components/dc-tables"
import {
  formatDate,
  formatDateYear,
  formatNumber,
} from "common/utils/formatters"
import { Panel } from "common/components/scaffold"
import { FileInput } from "common/components/input"
import {
  normalizeBiofuel,
  normalizeCountry,
  normalizeFeedstock,
  normalizeProductionSite,
} from "carbure/utils/normalizers"
import { usePortal } from "common/components/portal"
import { compact } from "common/utils/collection"

const DoubleCountingSettings = () => {
  const { t } = useTranslation()
  const rights = useRights()
  const entity = useEntity()
  const portal = usePortal()

  const agreements = useQuery(api.getDoubleCountingAgreements, {
    key: "dc-agreements",
    params: [entity.id],
  })

  const agreementsData = agreements.result?.data.data ?? []
  const isEmpty = agreementsData.length === 0
  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  function showAgreementDialog(dc: DoubleCounting) {
    portal((resolve) => (
      <DoubleCountingDialog
        entity={entity}
        agreementID={dc.id}
        onClose={resolve}
      />
    ))
  }

  function showUploadDialog() {
    portal((resolve) => (
      <DoubleCountingUploadDialog entity={entity} onClose={resolve} />
    ))
  }

  return (
    <Panel id="double-counting">
      <header>
        <h1>
          <Trans>Dossiers double comptage</Trans>
        </h1>
        {canModify && (
          <Button
            asideX
            variant="primary"
            icon={Plus}
            action={showUploadDialog}
            label={t("Ajouter un dossier double comptage")}
          />
        )}
      </header>

      {isEmpty && (
        <>
          <section>
            <Alert icon={AlertCircle} variant="warning">
              <Trans>Aucun dossier double comptage trouvé</Trans>
            </Alert>
          </section>
          <footer />
        </>
      )}

      {!isEmpty && (
        <Table
          rows={agreementsData}
          onAction={showAgreementDialog}
          columns={[
            {
              header: t("Statut"),
              cell: (dc) => <DoubleCountingStatus status={dc.status} />,
            },
            {
              header: t("Site de production"),
              cell: (dc) => <Cell text={dc.production_site} />,
            },
            {
              header: t("Période de validité"),
              cell: (dc) => (
                <Cell
                  text={`${formatDateYear(dc.period_start)} - ${formatDateYear(dc.period_end)}`} // prettier-ignore
                />
              ),
            },
            {
              header: t("Date de soumission"),
              cell: (dc) => <Cell text={formatDate(dc.creation_date)} />,
            },
          ]}
        />
      )}

      {agreements.loading && <LoaderOverlay />}
    </Panel>
  )
}

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
              <MailTo user="doublecompte" host="beta.gouv.fr">
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

type DoubleCountingUploadDialogProps = {
  entity: Entity
  onClose: () => void
}

const DoubleCountingUploadDialog = ({
  entity,
  onClose,
}: DoubleCountingUploadDialogProps) => {
  const { t } = useTranslation()

  const { value, bind } = useForm({
    productionSite: undefined as ProductionSite | undefined,
    doubleCountingFile: undefined as File | undefined,
    documentationFile: undefined as File | undefined,
  })

  const uploadFile = useMutation(api.uploadDoubleCountingFile)
  const uploadDocFile = useMutation(api.uploadDoubleCountingDescriptionFile)

  const disabled =
    !value.productionSite ||
    !value.doubleCountingFile ||
    !value.documentationFile

  async function submitAgreement() {
    if (
      !entity ||
      !value.productionSite ||
      !value.doubleCountingFile ||
      !value.documentationFile
    )
      return

    const res = await uploadFile.execute(
      entity.id,
      value.productionSite.id,
      value.doubleCountingFile
    )

    if (res.data.data) {
      await uploadDocFile.execute(
        entity.id,
        res.data.data.dca_id,
        value.documentationFile
      )
    }

    onClose()
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Création dossier double comptage")}</h1>
      </header>

      <main>
        <section>
          <Form id="dc-request">
            <p>
              <Trans>
                Dans un premier temps, renseignez le site de production concerné
                par votre demande.
              </Trans>
            </p>

            <AutoComplete
              autoFocus
              label={t("Site de production")}
              placeholder={t("Rechercher un site de production")}
              getOptions={(search) => findProductionSites(search, entity.id)}
              normalize={normalizeProductionSite}
              {...bind("productionSite")}
            />

            <p>
              <a href="/api/v3/doublecount/get-template">
                <Trans>Téléchargez le modèle depuis ce lien</Trans>
              </a>{" "}
              <Trans>
                puis remplissez les <b>deux premiers onglets</b> afin de
                détailler vos approvisionnements et productions sujets au double
                comptage. Ensuite, importez ce fichier avec le bouton ci-dessous
                :
              </Trans>
            </p>

            <FileInput
              icon={value.doubleCountingFile ? Check : Upload}
              label={t("Importer les informations double comptage")}
              {...bind("doubleCountingFile")}
            />

            <p>
              <Trans>
                Finalement, veuillez importer un fichier texte contenant la
                description de vos méthodes d'approvisionnement et de production
                ayant trait au double comptage.
              </Trans>
            </p>

            <FileInput
              icon={value.documentationFile ? Check : Upload}
              label={t("Importer la description")}
              {...bind("documentationFile")}
            />
          </Form>
        </section>
      </main>

      <footer>
        <Button
          asideX
          submit="dc-request"
          loading={uploadFile.loading || uploadDocFile.loading}
          disabled={disabled}
          variant="primary"
          icon={Check}
          action={submitAgreement}
          label={t("Soumettre le dossier")}
        />
        <Button icon={Return} action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

type DoubleCountingSourcingDialogProps = {
  add?: boolean
  dcaID: number
  sourcing?: DoubleCountingSourcing
  entity: Entity
  onClose: () => void
}

const DoubleCountingSourcingDialog = ({
  add,
  dcaID,
  sourcing,
  entity,
  onClose,
}: DoubleCountingSourcingDialogProps) => {
  const { t } = useTranslation()

  const { value, bind } = useForm<Partial<DoubleCountingSourcing>>(
    sourcing ?? {
      year: new Date().getFullYear(),
      feedstock: undefined,
      metric_tonnes: 0,
      origin_country: undefined,
      transit_country: undefined,
      supply_country: undefined,
    }
  )

  const addSourcing = useMutation(api.addDoubleCountingSourcing, {
    invalidates: ["dc-details"],
    onSuccess: () => onClose(),
  })

  const updateSourcing = useMutation(api.updateDoubleCountingSourcing, {
    invalidates: ["dc-details"],
  })

  async function saveSourcing() {
    if (
      !value.year ||
      !value.metric_tonnes ||
      !value.feedstock ||
      !value.origin_country ||
      !value.transit_country ||
      !value.supply_country
    ) {
      return
    }

    if (add) {
      await addSourcing.execute(
        entity.id,
        dcaID,
        value.year,
        value.metric_tonnes,
        value.feedstock.code,
        value.origin_country.code_pays,
        value.transit_country.code_pays,
        value.supply_country.code_pays
      )
    } else if (sourcing) {
      await updateSourcing.execute(entity.id, sourcing.id, value.metric_tonnes)
    }
  }

  const disabled =
    !value.year ||
    !value.metric_tonnes ||
    !value.feedstock ||
    !value.origin_country ||
    !value.transit_country ||
    !value.supply_country

  const loading = addSourcing.loading || updateSourcing.loading

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Approvisionnement")} </h1>
      </header>

      <main>
        <section>
          <p>
            {t(
              "Précisez les informations concernant votre approvisionnement en matière première dans le formularie ci-dessous."
            )}
          </p>
        </section>

        <section>
          <Form id="sourcing" onSubmit={saveSourcing}>
            <NumberInput
              autoFocus
              disabled={!add}
              label={t("Année")}
              {...bind("year")}
            />
            <AutoComplete
              disabled={!add}
              label={t("Matière première")}
              normalize={normalizeFeedstock}
              getOptions={(search) => findFeedstocks(search, true)}
              defaultOptions={compact([value.feedstock])}
              {...bind("feedstock")}
            />
            <NumberInput
              label={t("Poids en tonnes")}
              type="number"
              {...bind("metric_tonnes")}
            />
            <AutoComplete
              disabled={!add}
              label={t("Pays d'origine")}
              getOptions={findCountries}
              defaultOptions={compact([value.origin_country])}
              normalize={normalizeCountry}
              {...bind("origin_country")}
            />
            <AutoComplete
              disabled={!add}
              label={t("Pays de transit")}
              getOptions={findCountries}
              defaultOptions={compact([value.transit_country])}
              normalize={normalizeCountry}
              {...bind("transit_country")}
            />
            <AutoComplete
              disabled={!add}
              label={t("Pays d'approvisionnement")}
              getOptions={findCountries}
              defaultOptions={compact([value.supply_country])}
              normalize={normalizeCountry}
              {...bind("supply_country")}
            />
          </Form>
        </section>
      </main>

      <footer>
        <Button
          asideX
          disabled={disabled}
          submit="sourcing"
          variant="primary"
          loading={loading}
          icon={add ? Plus : Save}
        >
          {add ? (
            <Trans>Ajouter un approvisionnement</Trans>
          ) : (
            <Trans>Enregistrer les modifications</Trans>
          )}
        </Button>
        <Button icon={Return} action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

type DoubleCountingProductionDialogProps = {
  add?: boolean
  dcaID: number
  production?: DoubleCountingProduction
  entity: Entity
  onClose: () => void
}

const DoubleCountingProductionDialog = ({
  add,
  dcaID,
  production,
  onClose,
}: DoubleCountingProductionDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const { value, bind } = useForm<Partial<DoubleCountingProduction>>(
    production ?? {
      year: new Date().getFullYear(),
      feedstock: undefined,
      biofuel: undefined,
      estimated_production: 0,
      max_production_capacity: 0,
      requested_quota: 0,
    }
  )

  const addProduction = useMutation(api.addDoubleCountingProduction, {
    invalidates: ["dc-details"],
    onSuccess: () => onClose(),
  })

  const updateProduction = useMutation(api.updateDoubleCountingProduction, {
    invalidates: ["dc-details"],
  })

  async function saveProduction() {
    if (
      !value.year ||
      !value.feedstock ||
      !value.biofuel ||
      !value.requested_quota ||
      !value.estimated_production ||
      !value.max_production_capacity
    ) {
      return
    }

    if (add) {
      await addProduction.execute(
        entity.id,
        dcaID,
        value.year,
        value.feedstock.code,
        value.biofuel.code,
        value.estimated_production,
        value.max_production_capacity,
        value.requested_quota
      )
    } else if (production) {
      await updateProduction.execute(
        entity.id,
        production.id,
        value.estimated_production,
        value.max_production_capacity,
        value.requested_quota
      )
    }
  }

  const disabled =
    !value.year ||
    !value.feedstock ||
    !value.biofuel ||
    !value.requested_quota ||
    !value.estimated_production ||
    !value.max_production_capacity

  const loading = addProduction.loading || updateProduction.loading

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Production")}</h1>
      </header>
      <main>
        <section>
          <p>
            {t(
              "Précisez les informations concernant votre production de biocarburant dans le formularie ci-dessous."
            )}
          </p>
        </section>
        <section>
          <Form id="dc-production" onSubmit={saveProduction}>
            <NumberInput
              autoFocus
              disabled={!add}
              label={t("Année")}
              {...bind("year")}
            />
            <AutoComplete
              disabled={!add}
              label={t("Matière première")}
              normalize={normalizeFeedstock}
              getOptions={(search) => findFeedstocks(search, true)}
              defaultOptions={compact([value.feedstock])}
              {...bind("feedstock")}
            />
            <AutoComplete
              disabled={!add}
              label={t("Biocarburant")}
              getOptions={findBiofuels}
              defaultOptions={compact([value.biofuel])}
              normalize={normalizeBiofuel}
              {...bind("biofuel")}
            />
            <NumberInput
              label={t("Production maximale")}
              type="number"
              {...bind("max_production_capacity")}
            />
            <NumberInput
              label={t("Production estimée")}
              type="number"
              {...bind("estimated_production")}
            />
            <NumberInput
              label={t("Quota demandé")}
              type="number"
              {...bind("requested_quota")}
            />
          </Form>
        </section>
      </main>
      <footer>
        <Button
          asideX
          disabled={disabled}
          submit="dc-production"
          variant="primary"
          loading={loading}
          icon={add ? Plus : Save}
        >
          {add ? (
            <Trans>Ajouter une production</Trans>
          ) : (
            <Trans>Enregistrer les modifications</Trans>
          )}
        </Button>
        <Button icon={Return} action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

type QuotasTableProps = {
  entity: Entity
  agreement: DoubleCounting | undefined
}

const QuotasTable = ({ entity, agreement }: QuotasTableProps) => {
  const { t } = useTranslation()

  const entityID = entity?.id ?? -1
  const dcaID = agreement?.id ?? -1

  const details = useQuery(api.getQuotaDetails, {
    key: "quota-details",
    params: [entityID, dcaID],
  })

  const columns: Column<QuotaDetails>[] = [
    {
      header: t("Biocarburant"),
      cell: (d) => <Cell text={d.biofuel.name} />,
    },
    {
      header: t("Matière première"),
      cell: (d) => <Cell text={d.feedstock.name} />,
    },
    { header: t("Nombre de lots"), cell: (d) => d.nb_lots },
    {
      header: t("Volume produit"),
      cell: (d) => (
        <Cell
          text={`${formatNumber(d.volume)} L`}
          sub={`${d.current_production_weight_sum_tonnes} t`}
        />
      ),
    },
    {
      header: t("Quota approuvé"),
      cell: (d) => <Cell text={formatNumber(d.approved_quota)} />,
    },
    {
      header: t("Progression des quotas"),
      cell: (d) => (
        <progress
          max={d.approved_quota}
          value={d.current_production_weight_sum_tonnes}
          title={`${d.current_production_weight_sum_tonnes} / ${d.approved_quota}`}
        />
      ),
    },
  ]

  const rows = details.result?.data.data ?? []
  return <Table loading={details.loading} columns={columns} rows={rows} />
}

export default DoubleCountingSettings
