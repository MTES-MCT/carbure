import { Trans, useTranslation } from "react-i18next"
import { useEffect, useState } from "react"
import cl from "clsx"
import statusStyles from "transactions/components/status.module.css"
import styles from "./settings.module.css"
import { EntitySelection } from "carbure/hooks/use-entity"
import { CompanySettingsHook as DoubleContingSettingsHook } from "../hooks/use-company"
import {
  DoubleCounting,
  DoubleCountingStatus,
  ProductionSite,
  UserRole,
  DoubleCountingSourcing,
  DoubleCountingProduction,
} from "common/types"
import { Title, LoaderOverlay, Box } from "common/components"
import { SectionHeader, SectionBody, Section } from "common/components/section"
import { useRights } from "carbure/hooks/use-rights"
import Table, { Actions, Column, Row } from "common/components/table"
import { AsyncButton, Button } from "common/components/button"
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
import {
  confirm,
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  prompt,
  PromptProps,
} from "common/components/dialog"
import { formatDate, YEAR_ONLY } from "./common"
import {
  findBiocarburants,
  findCountries,
  findMatieresPremieres,
  findProductionSites,
} from "common/api"
import { LabelAutoComplete } from "common/components/autocomplete"
import * as api from "../api"
import useAPI from "common/hooks/use-api"
import { padding } from "transactions/components/list-columns"
import Tabs from "common/components/tabs"
import { Form } from "common/components/form"
import { LabelInput } from "common/components/input"
import useForm from "common/hooks/use-form"
import YearTable from "doublecount/components/year-table"

export const DCStatus = ({ status }: { status: DoubleCountingStatus }) => {
  const { t } = useTranslation()

  const statusLabels = {
    [DoubleCountingStatus.Pending]: t("En attente"),
    [DoubleCountingStatus.Accepted]: t("Accepté"),
    [DoubleCountingStatus.Rejected]: t("Refusé"),
    [DoubleCountingStatus.Lapsed]: t("Expiré"),
  }

  return (
    <span
      className={cl(
        styles.settingsStatus,
        statusStyles.status,
        statusStyles.smallStatus,
        status === DoubleCountingStatus.Accepted && statusStyles.statusAccepted,
        status === DoubleCountingStatus.Pending && statusStyles.statusWaiting,
        status === DoubleCountingStatus.Rejected && statusStyles.statusRejected,
        status === DoubleCountingStatus.Lapsed && statusStyles.statusToFix
      )}
    >
      {statusLabels[status]}
    </span>
  )
}

type DoubleCountingUploadPromptProps = PromptProps<void> & {
  entity: EntitySelection
}

const DoubleCountingUploadPrompt = ({
  entity,
  onResolve,
}: DoubleCountingUploadPromptProps) => {
  const { t } = useTranslation()

  const [productionSite, setProductionSite] = useState<ProductionSite | null>(null) // prettier-ignore
  const [doubleCountingFile, setDoubleCountingFile] = useState<File | null>(null) // prettier-ignore
  const [documentationFile, setDocumentationFile] = useState<File | null>(null) // prettier-ignore

  const [uploading, uploadFile] = useAPI(api.uploadDoubleCountingFile)
  const [uploadingDoc, uploadDocFile] = useAPI(
    api.uploadDoubleCountingDescriptionFile
  )

  const disabled = !productionSite || !doubleCountingFile || !documentationFile

  async function submitAgreement() {
    if (!entity || !productionSite || !doubleCountingFile || !documentationFile)
      return

    const res = await uploadFile(
      entity.id,
      productionSite.id,
      doubleCountingFile
    )
    res && (await uploadDocFile(entity.id, res.dca_id, documentationFile))

    onResolve()
  }

  return (
    <Dialog onResolve={onResolve} className={styles.settingsPrompt}>
      <DialogTitle text={t("Création dossier double comptage")} />

      <Form>
        <div className={styles.settingsText}>
          <Trans>
            Dans un premier temps, renseignez le site de production concerné par
            votre demande.
          </Trans>
        </div>

        <LabelAutoComplete
          label={t("Site de production")}
          placeholder={t("Rechercher un site de production")}
          className={styles.settingsField}
          value={productionSite}
          onChange={(e: any) => setProductionSite(e.target.value)}
          getQuery={findProductionSites}
          getValue={(ps: any) => ps.id}
          getLabel={(ps: any) => ps.name}
          queryArgs={[entity?.id]}
          minLength={0}
        />

        <div className={styles.settingsText}>
          <a
            href="/api/v3/doublecount/get-template"
            className={styles.settingsLink}
          >
            <Trans>Téléchargez le modèle depuis ce lien</Trans>
          </a>
          <Trans>
            puis remplissez les <b>deux premiers onglets</b> afin de détailler
            vos approvisionnements et productions sujets au double comptage.
            Ensuite, importez ce fichier avec le bouton ci-dessous :
          </Trans>
        </div>

        <Button
          as="label"
          level={doubleCountingFile ? "success" : "primary"}
          icon={doubleCountingFile ? Check : Upload}
          className={styles.settingsFormButton}
        >
          {doubleCountingFile ? (
            doubleCountingFile.name
          ) : (
            <Trans>Importer les informations double comptage</Trans>
          )}
          <input
            type="file"
            className={styles.importFileInput}
            onChange={(e) => setDoubleCountingFile(e!.target.files![0])}
          />
        </Button>

        <div className={styles.settingsText}>
          <Trans>
            Finalement, veuillez importer un fichier texte contenant la
            description de vos méthodes d'approvisionnement et de production
            ayant trait au double comptage.
          </Trans>
        </div>

        <Button
          as="label"
          level={documentationFile ? "success" : "primary"}
          icon={documentationFile ? Check : Upload}
          className={styles.settingsFormButton}
        >
          {documentationFile ? (
            documentationFile.name
          ) : (
            <Trans>Importer la description</Trans>
          )}
          <input
            type="file"
            className={styles.importFileInput}
            onChange={(e) => setDocumentationFile(e!.target.files![0])}
          />
        </Button>

        <DialogButtons>
          <AsyncButton
            loading={uploading.loading || uploadingDoc.loading}
            disabled={disabled}
            level="primary"
            icon={Check}
            onClick={submitAgreement}
          >
            <Trans>Soumettre le dossier</Trans>
          </AsyncButton>
          <Button icon={Return} onClick={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </Form>
    </Dialog>
  )
}

type DoubleCountingSourcingPromptProps = PromptProps<true | void> & {
  add?: boolean
  dcaID: number
  sourcing?: DoubleCountingSourcing
  entity: EntitySelection
}

const DoubleCountingSourcingPrompt = ({
  add,
  dcaID,
  sourcing,
  entity,
  onResolve,
}: DoubleCountingSourcingPromptProps) => {
  const { t } = useTranslation()

  const { data, onChange } = useForm<Partial<DoubleCountingSourcing>>(
    sourcing ?? {
      year: new Date().getFullYear(),
      feedstock: undefined,
      metric_tonnes: 0,
      origin_country: undefined,
      transit_country: undefined,
      supply_country: undefined,
    }
  )

  const [adding, addSourcing] = useAPI(api.addDoubleCountingSourcing)
  const [updating, updateSourcing] = useAPI(api.updateDoubleCountingSourcing)

  async function saveSourcing() {
    if (
      entity === null ||
      !data.year ||
      !data.metric_tonnes ||
      !data.feedstock ||
      !data.origin_country ||
      !data.transit_country ||
      !data.supply_country
    )
      return

    if (add) {
      await addSourcing(
        entity.id,
        dcaID,
        data.year,
        data.metric_tonnes,
        data.feedstock.code,
        data.origin_country.code_pays,
        data.transit_country.code_pays,
        data.supply_country.code_pays
      )
    } else if (sourcing) {
      await updateSourcing(entity.id, sourcing.id, data.metric_tonnes)
    }

    onResolve(true)
  }

  const loading = adding.loading || updating.loading

  return (
    <Dialog onResolve={onResolve} className={styles.settingsPrompt}>
      <DialogTitle text={t("Approvisionnement")} />
      <DialogText
        text={t(
          "Précisez les informations concernant votre approvisionnement en matière première dans le formularie ci-dessous."
        )}
      />

      <Form className={styles.settingsForm} onSubmit={saveSourcing}>
        <LabelInput
          disabled={!add}
          label={t("Année")}
          name="year"
          value={data.year}
          onChange={onChange}
        />
        <LabelAutoComplete
          disabled={!add}
          name="feedstock"
          label={t("Matière première")}
          minLength={0}
          value={data.feedstock}
          onChange={onChange}
          getValue={(mp) => mp.code}
          getLabel={(mp) => t(mp.code, { ns: "feedstocks" })}
          getQuery={findMatieresPremieres}
          queryArgs={[true]}
        />
        <LabelInput
          label={t("Poids en tonnes")}
          type="number"
          name="metric_tonnes"
          value={data.metric_tonnes}
          onChange={onChange}
        />
        <LabelAutoComplete
          disabled={!add}
          name="origin_country"
          label={t("Pays d'origine")}
          value={data.origin_country}
          getValue={(c) => c.code_pays}
          getLabel={(c) => t(c.code_pays, { ns: "countries" })}
          getQuery={findCountries}
          onChange={onChange}
        />
        <LabelAutoComplete
          disabled={!add}
          name="transit_country"
          label={t("Pays de transit")}
          value={data.transit_country}
          getValue={(c) => c.code_pays}
          getLabel={(c) => t(c.code_pays, { ns: "countries" })}
          getQuery={findCountries}
          onChange={onChange}
        />
        <LabelAutoComplete
          disabled={!add}
          name="supply_country"
          label={t("Pays d'approvisionnement")}
          value={data.supply_country}
          getValue={(c) => c.code_pays}
          getLabel={(c) => t(c.code_pays, { ns: "countries" })}
          getQuery={findCountries}
          onChange={onChange}
        />

        <DialogButtons>
          <AsyncButton
            submit
            level="primary"
            loading={loading}
            icon={add ? Plus : Save}
          >
            {add ? (
              <Trans>Ajouter un approvisionnement</Trans>
            ) : (
              <Trans>Enregistrer les modifications</Trans>
            )}
          </AsyncButton>
          <Button icon={Return} onClick={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </Form>
    </Dialog>
  )
}

type DoubleCountingProductionPromptProps = PromptProps<true | void> & {
  add?: boolean
  dcaID: number
  production?: DoubleCountingProduction
  entity: EntitySelection
}

const DoubleCountingProductionPrompt = ({
  add,
  dcaID,
  production,
  entity,
  onResolve,
}: DoubleCountingProductionPromptProps) => {
  const { t } = useTranslation()

  const { data, onChange } = useForm<Partial<DoubleCountingProduction>>(
    production ?? {
      year: new Date().getFullYear(),
      feedstock: undefined,
      biofuel: undefined,
      estimated_production: 0,
      max_production_capacity: 0,
      requested_quota: 0,
    }
  )

  const [adding, addProduction] = useAPI(api.addDoubleCountingProduction)
  const [updating, updateProduction] = useAPI(
    api.updateDoubleCountingProduction
  )

  async function saveProduction() {
    if (
      entity === null ||
      !data.year ||
      !data.feedstock ||
      !data.biofuel ||
      !data.requested_quota ||
      !data.estimated_production ||
      !data.max_production_capacity
    )
      return

    if (add) {
      await addProduction(
        entity.id,
        dcaID,
        data.year,
        data.feedstock.code,
        data.biofuel.code,
        data.estimated_production,
        data.max_production_capacity,
        data.requested_quota
      )
    } else if (production) {
      await updateProduction(
        entity.id,
        production.id,
        data.estimated_production,
        data.max_production_capacity,
        data.requested_quota
      )
    }

    onResolve(true)
  }

  const loading = adding.loading || updating.loading

  return (
    <Dialog onResolve={onResolve} className={styles.settingsPrompt}>
      <DialogTitle text={t("Approvisionnement")} />
      <DialogText
        text={t(
          "Précisez les informations concernant votre approvisionnement en matière première dans le formularie ci-dessous."
        )}
      />

      <Form className={styles.settingsForm} onSubmit={saveProduction}>
        <LabelInput
          disabled={!add}
          label={t("Année")}
          name="year"
          value={data.year}
          onChange={onChange}
        />
        <LabelAutoComplete
          disabled={!add}
          name="feedstock"
          label={t("Matière première")}
          minLength={0}
          value={data.feedstock}
          onChange={onChange}
          getValue={(mp) => mp.code}
          getLabel={(mp) => t(mp.code, { ns: "feedstocks" })}
          getQuery={findMatieresPremieres}
          queryArgs={[true]}
        />
        <LabelAutoComplete
          disabled={!add}
          name="biofuel"
          label={t("Biocarburant")}
          minLength={0}
          value={data.biofuel}
          onChange={onChange}
          getValue={(bc) => bc.code}
          getLabel={(bc) => t(bc.code, { ns: "biofuels" })}
          getQuery={findBiocarburants}
        />
        <LabelInput
          label={t("Production maximale")}
          type="number"
          name="max_production_capacity"
          value={data.max_production_capacity}
          onChange={onChange}
        />
        <LabelInput
          label={t("Production estimée")}
          type="number"
          name="estimated_production"
          value={data.estimated_production}
          onChange={onChange}
        />
        <LabelInput
          label={t("Quota demandé")}
          type="number"
          name="requested_quota"
          value={data.requested_quota}
          onChange={onChange}
        />

        <DialogButtons>
          <AsyncButton
            submit
            level="primary"
            loading={loading}
            icon={add ? Plus : Save}
          >
            {add ? (
              <Trans>Ajouter une production</Trans>
            ) : (
              <Trans>Enregistrer les modifications</Trans>
            )}
          </AsyncButton>
          <Button icon={Return} onClick={() => onResolve()}>
            <Trans>Annuler</Trans>
          </Button>
        </DialogButtons>
      </Form>
    </Dialog>
  )
}

type DoubleCountingPromptProps = PromptProps<any> & {
  entity: EntitySelection
  agreementID: number
}

const DoubleCountingPrompt = ({
  entity,
  agreementID,
  onResolve,
}: DoubleCountingPromptProps) => {
  const { t } = useTranslation()

  const [focus, setFocus] = useState("sourcing")

  const [agreement, getAgreement] = useAPI(api.getDoubleCountingDetails)
  const [, deleteSourcing] = useAPI(api.deleteDoubleCountingSourcing)
  const [, deleteProduction] = useAPI(api.deleteDoubleCountingProduction)

  useEffect(() => {
    if (entity) {
      getAgreement(entity.id, agreementID)
    }
  }, [entity, agreementID, getAgreement])

  const dcaID = agreement.data?.id ?? -1
  const dcaStatus = agreement.data?.status ?? DoubleCountingStatus.Pending

  const isFinal = agreement.data?.status !== DoubleCountingStatus.Pending

  function reloadAgreement() {
    if (entity === null) return
    getAgreement(entity.id, agreementID)
  }

  async function removeSourcingRow(sourcingID: number) {
    if (!entity || isFinal) return

    const ok = await confirm(
      t("Supprimer approvisionnement"),
      t("Voulez-vous supprimer cette ligne d'approvisionnement ?")
    )

    if (ok) {
      await deleteSourcing(entity.id, sourcingID)
      reloadAgreement()
    }
  }

  async function removeProductionRow(productionID: number) {
    if (!entity || isFinal) return

    const ok = await confirm(
      t("Supprimer production"),
      t("Voulez-vous supprimer cette ligne de production ?")
    )

    if (ok) {
      await deleteProduction(entity.id, productionID)
      reloadAgreement()
    }
  }

  const sourcingColumns: Column<DoubleCountingSourcing>[] = [
    padding,
    {
      header: t("Matière première"),
      render: (s) => t(s.feedstock.code, { ns: "feedstocks" }),
    },
    {
      header: t("Poids en tonnes"),
      render: (s) => s.metric_tonnes,
    },
    {
      header: t("Origine"),
      render: (s) => t(s.origin_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Approvisionnement"),
      render: (s) =>
        s.supply_country && t(s.supply_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Transit"),
      render: (s) =>
        s.transit_country &&
        t(s.transit_country.code_pays, { ns: "countries" }),
    },
    padding,
  ]

  if (!isFinal) {
    sourcingColumns.splice(
      -1,
      0,
      Actions((s) => [
        {
          icon: Cross,
          action: () => removeSourcingRow(s.id),
          title: t("Supprimer approvisionnement"),
        },
      ])
    )
  }

  const sourcingRows: Row<DoubleCountingSourcing>[] = (
    agreement.data?.sourcing ?? []
  ).map((s) => ({
    value: s,
    onClick: isFinal
      ? undefined
      : async () => {
          const ok = await prompt((resolve) => (
            <DoubleCountingSourcingPrompt
              entity={entity}
              dcaID={dcaID}
              sourcing={s}
              onResolve={resolve}
            />
          ))

          ok && reloadAgreement()
        },
  }))

  const productionColumns: Column<DoubleCountingProduction>[] = [
    padding,
    {
      header: t("Matière première"),
      render: (p) => t(p.feedstock.code, { ns: "feedstocks" }),
    },
    {
      header: t("Biocarburant"),
      render: (p) => t(p.biofuel.code, { ns: "biofuels" }),
    },
    {
      header: t("Prod. max"),
      render: (p) => p.max_production_capacity,
    },
    {
      header: t("Prod. estimée"),
      render: (p) => p.estimated_production,
    },
    {
      header: t("Quota demandé"),
      render: (p) => p.requested_quota,
    },
    {
      header: t("Quota approuvé"),
      render: (p) =>
        p.approved_quota === -1 ? t("En attente") : p.approved_quota,
    },
    padding,
  ]

  if (!isFinal) {
    productionColumns.splice(
      -1,
      0,
      Actions((s) => [
        {
          icon: Cross,
          action: () => removeProductionRow(s.id),
          title: t("Supprimer production"),
        },
      ])
    )
  }

  const productionRows: Row<DoubleCountingProduction>[] = (
    agreement.data?.production ?? []
  ).map((p) => ({
    value: p,
    onClick: isFinal
      ? undefined
      : async () => {
          const ok = await prompt((resolve) => (
            <DoubleCountingProductionPrompt
              entity={entity}
              dcaID={dcaID}
              production={p}
              onResolve={resolve}
            />
          ))

          ok && reloadAgreement()
        },
  }))

  const excelURL =
    agreement.data &&
    `/api/v3/doublecount/agreement?dca_id=${agreement.data.id}&entity_id=${entity?.id}&export=true`
  const documentationURL =
    entity &&
    agreement.data &&
    agreement.data.documents[0] &&
    `/api/v3/doublecount/download-documentation?entity_id=${entity.id}&dca_id=${agreement.data.id}&file_id=${agreement.data.documents[0].id}`

  return (
    <Dialog wide onResolve={onResolve} className={styles.settingsPrompt}>
      <Box row>
        <DCStatus status={dcaStatus} />
        <DialogTitle text={t("Dossier double comptage")} />
      </Box>

      <Tabs
        tabs={[
          { key: "sourcing", label: t("Approvisionnement") },
          { key: "production", label: t("Production") },
        ]}
        focus={focus}
        onFocus={setFocus}
      />

      {focus === "sourcing" && (
        <div className={styles.modalTableContainer}>
          <YearTable columns={sourcingColumns} rows={sourcingRows} />

          {!isFinal && (
            <span
              className={styles.modalTableAddRow}
              onClick={async () => {
                const ok = await prompt((resolve) => (
                  <DoubleCountingSourcingPrompt
                    add
                    dcaID={dcaID}
                    entity={entity}
                    onResolve={resolve}
                  />
                ))

                ok && reloadAgreement()
              }}
            >
              <Trans>+ Ajouter une ligne d'approvisionnement</Trans>
            </span>
          )}
        </div>
      )}

      {focus === "production" && (
        <div className={styles.modalTableContainer}>
          <YearTable columns={productionColumns} rows={productionRows} />

          {!isFinal && (
            <span
              className={styles.modalTableAddRow}
              onClick={async () => {
                await prompt((resolve) => (
                  <DoubleCountingProductionPrompt
                    add
                    dcaID={dcaID}
                    entity={entity}
                    onResolve={resolve}
                  />
                ))

                reloadAgreement()
              }}
            >
              <Trans>+ Ajouter une ligne de production</Trans>
            </span>
          )}
        </div>
      )}

      <DialogButtons>
        <Box style={{ marginRight: "auto" }}>
          <a
            href={excelURL ?? "#"}
            target="_blank"
            rel="noreferrer"
            className={styles.settingsBottomLink}
          >
            <Upload />
            <Trans>Télécharger le dossier au format excel</Trans>
          </a>
          <a
            href={documentationURL ?? "#"}
            target="_blank"
            rel="noreferrer"
            className={styles.settingsBottomLink}
          >
            <Upload />
            <Trans>Télécharger la description de l'activité</Trans>
          </a>
        </Box>

        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Retour</Trans>
        </Button>
      </DialogButtons>

      {agreement.loading && <LoaderOverlay />}
    </Dialog>
  )
}

type DoubleCountingSettingsProps = {
  entity: EntitySelection
  settings: DoubleContingSettingsHook
}

const DoubleCountingSettings = ({
  entity,
  settings,
}: DoubleCountingSettingsProps) => {
  const { t } = useTranslation()
  const rights = useRights()

  const [agreements, getAgreements] = useAPI(api.getDoubleCountingAgreements)

  useEffect(() => {
    if (entity) {
      getAgreements(entity.id)
    }
  }, [entity, getAgreements])

  const isEmpty = !agreements.data || agreements.data.length === 0
  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  const columns: Column<DoubleCounting>[] = [
    padding,
    {
      header: t("Statut"),
      render: (dc) => <DCStatus status={dc.status} />,
    },
    {
      header: t("Site de production"),
      render: (dc) => dc.production_site,
    },
    {
      header: t("Période de validité"),
      render: (dc) =>
        `${formatDate(dc.period_start, YEAR_ONLY)} - ${formatDate(
          dc.period_end,
          YEAR_ONLY
        )}`,
    },
    {
      header: t("Date de soumission"),
      render: (dc) => formatDate(dc.creation_date),
    },
    padding,
  ]

  const rows: Row<DoubleCounting>[] = (agreements.data ?? []).map((dc) => ({
    value: dc,
    onClick: () =>
      prompt((resolve) => (
        <DoubleCountingPrompt
          entity={entity}
          agreementID={dc.id}
          onResolve={resolve}
        />
      )),
  }))

  return (
    <Section id="double-counting">
      <SectionHeader>
        <Title>
          <Trans>Dossiers double comptage</Trans>
        </Title>
        {canModify && (
          <Button
            level="primary"
            icon={Plus}
            onClick={async () => {
              if (entity === null) return

              await prompt((resolve) => (
                <DoubleCountingUploadPrompt
                  entity={entity}
                  onResolve={resolve}
                />
              ))

              getAgreements(entity.id)
            }}
          >
            <Trans>Ajouter un dossier double comptage</Trans>
          </Button>
        )}
      </SectionHeader>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            <Trans>Aucun dossier double comptage trouvé</Trans>
          </Alert>
        </SectionBody>
      )}

      {!isEmpty && (
        <Table columns={columns} rows={rows} className={styles.settingsTable} />
      )}

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default DoubleCountingSettings
