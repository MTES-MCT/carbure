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
import { Title, LoaderOverlay } from "common/components"
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
import { formatDate, SettingsForm } from "./common"
import {
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
import * as Fields from "transactions/components/form/fields"
import useForm from "common/hooks/use-form"

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

  const [productionSite, setProductionSite] = useState<ProductionSite | null>(
    null
  )

  const [sourcingFile, setSourcingFile] = useState<File | null>(null)
  const [productionFile, setProductionFile] = useState<File | null>(null)

  const [uploadingSourcing, uploadSourcing] = useAPI(
    api.uploadDoubleCountingSourcing
  )
  const [uploadingProduction, uploadProduction] = useAPI(
    api.uploadDoubleCountingProduction
  )

  const loading = uploadingSourcing.loading || uploadingProduction.loading
  const disabled = !productionSite || !sourcingFile || !productionFile

  async function submitAgreement() {
    if (!entity || !productionSite || !sourcingFile || !productionFile) return

    await uploadSourcing(entity.id, productionSite.id, sourcingFile)
    await uploadProduction(entity.id, productionSite.id, productionFile)

    onResolve()
  }

  return (
    <Dialog onResolve={onResolve} className={styles.settingsPrompt}>
      <DialogTitle text={t("Création dossier double comptage")} />

      <SettingsForm>
        <div className={styles.settingsText}>
          <Trans>
            Commencez dans un premier temps par renseigner le site de production
            concerné par votre demande.
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
            href="/api/v3/doublecount/get-template?file_type=SOURCING"
            className={styles.settingsLink}
          >
            <Trans>Téléchargez ce modèle</Trans>
          </a>
          <Trans>
            {" "}
            afin de renseigner les différentes sources d'approvisionnement en
            matières premières sujettes au double comptage.
          </Trans>
        </div>

        <Button
          as="label"
          level={sourcingFile ? "success" : "primary"}
          icon={sourcingFile ? Check : Upload}
          className={styles.settingsFormButton}
        >
          {sourcingFile ? (
            sourcingFile.name
          ) : (
            <Trans>Importer les informations d'approvisionnement</Trans>
          )}
          <input
            type="file"
            className={styles.importFileInput}
            onChange={(e) => setSourcingFile(e!.target.files![0])}
          />
        </Button>

        <div className={styles.settingsText}>
          <a
            href="/api/v3/doublecount/get-template?file_type=PRODUCTION"
            className={styles.settingsLink}
          >
            <Trans>Téléchargez ce modèle</Trans>
          </a>
          <Trans>
            {" "}
            pour lister la partie de votre production basée sur les matières
            premières sujettes au double comptage.
          </Trans>
        </div>

        <Button
          as="label"
          level={productionFile ? "success" : "primary"}
          icon={productionFile ? Check : Upload}
          className={styles.settingsFormButton}
        >
          {productionFile ? (
            productionFile.name
          ) : (
            <Trans>Importer les objectifs de production</Trans>
          )}
          <input
            type="file"
            className={styles.importFileInput}
            onChange={(e) => setProductionFile(e!.target.files![0])}
          />
        </Button>

        <DialogButtons>
          <AsyncButton
            loading={loading}
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
      </SettingsForm>
    </Dialog>
  )
}

type DoubleCountingSourcingPromptProps = PromptProps<void> & {
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

  function saveSourcing() {
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
      addSourcing(
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
      updateSourcing(
        entity.id,
        sourcing.id,
        dcaID,
        data.year,
        data.metric_tonnes,
        data.feedstock.code,
        data.origin_country.code_pays,
        data.transit_country.code_pays,
        data.supply_country.code_pays
      )
    }

    onResolve()
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

      <Form className={styles.settingsForm}>
        <LabelInput
          label={t("Année")}
          name="year"
          value={data.year}
          onChange={onChange}
        />
        <LabelAutoComplete
          name="feedstock"
          label={t("Matière première")}
          minLength={0}
          value={data.feedstock}
          getValue={(mp) => mp.code}
          getLabel={(mp) => t(mp.code, { ns: "feedstocks" })}
          getQuery={findMatieresPremieres}
        />
        <LabelInput
          label={t("Poids en tonnes")}
          type="number"
          name="metric_tonnes"
          value={data.metric_tonnes}
          onChange={onChange}
        />
        <LabelAutoComplete
          label={t("Pays d'origine")}
          value={data.origin_country}
          getValue={(c) => c.code_pays}
          getLabel={(c) => t(c.code_pays, { ns: "countries" })}
          getQuery={findCountries}
        />
        <LabelAutoComplete
          name="transit_country"
          label={t("Pays de transit")}
          value={data.transit_country}
          getValue={(c) => c.code_pays}
          getLabel={(c) => t(c.code_pays, { ns: "countries" })}
          getQuery={findCountries}
        />
        <LabelAutoComplete
          name="supply_country"
          label={t("Pays d'approvisionnement")}
          value={data.supply_country}
          getValue={(c) => c.code_pays}
          getLabel={(c) => t(c.code_pays, { ns: "countries" })}
          getQuery={findCountries}
        />
      </Form>

      <DialogButtons>
        <AsyncButton
          level="primary"
          loading={loading}
          icon={add ? Plus : Save}
          onClick={saveSourcing}
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

  const dcaID = agreement.data?.id ?? -1

  async function removeSourcingRow(sourcingID: number) {
    if (!entity) return

    const ok = await confirm(
      t("Supprimer approvisionnement"),
      t("Voulez-vous supprimer cette ligne d'approvisionnement ?")
    )

    if (ok) {
      deleteSourcing(entity.id, sourcingID)
    }
  }

  useEffect(() => {
    if (entity) {
      getAgreement(entity.id, agreementID)
    }
  }, [entity, agreementID, getAgreement])

  const sourcingColumns: Column<DoubleCountingSourcing>[] = [
    padding,
    {
      header: t("Année"),
      render: (s) => s.year,
    },
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
      render: (s) => t(s.supply_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Transit"),
      render: (s) => t(s.transit_country.code_pays, { ns: "countries" }),
    },
    Actions((s) => [
      {
        icon: Cross,
        action: () => removeSourcingRow(s.id),
        title: t("Supprimer approvisionnement"),
      },
    ]),
    padding,
  ]

  const sourcingRows: Row<DoubleCountingSourcing>[] = (
    agreement.data?.sourcing ?? []
  ).map((s) => ({
    value: s,
    onClick: () =>
      prompt((resolve) => (
        <DoubleCountingSourcingPrompt
          entity={entity}
          dcaID={dcaID}
          sourcing={s}
          onResolve={resolve}
        />
      )),
  }))

  const productionColumns: Column<DoubleCountingProduction>[] = [
    padding,
    {
      header: t("Année"),
      render: (p) => p.year,
    },
    {
      header: t("Matière première"),
      render: (p) => t(p.feedstock.code, { ns: "feedstocks" }),
    },
    {
      header: t("Biocarburant"),
      render: (p) => t(p.biofuel.code, { ns: "biofuels" }),
    },
    {
      header: t("Production max."),
      render: (p) => p.max_production_capacity,
    },
    {
      header: t("Production estimée"),
      render: (p) => p.estimated_production,
    },
    {
      header: t("Quota demandé"),
      render: (p) => p.requested_quota,
    },
    {
      header: t("Quota approuvé"),
      render: (p) => p.approved_quota,
    },
    padding,
  ]

  const productionRows: Row<DoubleCountingProduction>[] = (
    agreement.data?.production ?? []
  ).map((p) => ({ value: p }))

  return (
    <Dialog wide onResolve={onResolve} className={styles.settingsPrompt}>
      <DialogTitle text={t("Dossier double comptage")} />

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
          <Table columns={sourcingColumns} rows={sourcingRows} />
          <span
            className={styles.modalTableAddRow}
            onClick={() =>
              prompt((resolve) => (
                <DoubleCountingSourcingPrompt
                  add
                  dcaID={dcaID}
                  entity={entity}
                  onResolve={resolve}
                />
              ))
            }
          >
            <Trans>+ Ajouter une ligne d'approvisionnement</Trans>
          </span>
        </div>
      )}

      {focus === "production" && (
        <div className={styles.modalTableContainer}>
          <Table columns={productionColumns} rows={productionRows} />
        </div>
      )}

      <DialogButtons>
        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Annuler</Trans>
        </Button>
      </DialogButtons>
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
      header: t("Valide jusqu'au"),
      render: (dc) => formatDate(dc.period_end),
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
