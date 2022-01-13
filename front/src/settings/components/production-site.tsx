import { Trans, useTranslation } from "react-i18next"

import {
  Biocarburant,
  Country,
  GESOption,
  MatierePremiere,
  ProductionSiteDetails,
  UserRole,
  Certificate,
} from "common/types"

import { ProductionSiteSettingsHook } from "../hooks/use-production-sites"
import { Entity } from "carbure/types"

import styles from "./settings.module.css"

import * as common from "common/api"
import useForm from "common/hooks/use-form"

import { Title, Box, LoaderOverlay } from "common/components"
import { LabelInput, Label, LabelCheckbox } from "common/components/input"
import { Button } from "common/components/button"
import {
  AlertCircle,
  Cross,
  Plus,
  Return,
  Save,
} from "common-v2/components/icons"
import { Alert } from "common/components/alert"
import Table, {
  Actions,
  arrow,
  Column,
  Line,
  Row,
  padding,
} from "common/components/table"
import { SectionHeader, SectionBody, Section } from "common/components/section"
import {
  Dialog,
  DialogButtons,
  DialogText,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import {
  LabelAutoComplete,
  MultiAutocomplete,
} from "common/components/autocomplete"
import RadioGroup from "common/components/radio-group"
import { formatDate, SettingsForm } from "./common"
import { getMyCertificates } from "../api-v2"
import { useRights } from "carbure/hooks/entity"

export type ProductionSiteState = {
  // site
  site_id: string
  name: string
  date_mise_en_service: string
  ges_option: GESOption

  // double counting
  eligible_dc: boolean
  dc_reference: string

  // address
  city: string
  postal_code: string
  country: Country | null

  // manager
  manager_name: string
  manager_phone: string
  manager_email: string

  // input/output
  matieres_premieres: MatierePremiere[]
  biocarburants: Biocarburant[]

  // certificates
  certificates: Certificate[]
}

type ProductionSitePromptProps = PromptProps<ProductionSiteState> & {
  title: string
  description?: string
  entity: Entity | null
  productionSite?: ProductionSiteDetails
  readOnly?: boolean
}

// ville/code postal/addresse/pays numéro d'identification (SIRET), nom/prénom/téléphone/mail du gérant

export const ProductionSitePrompt = ({
  title,
  description,
  entity,
  productionSite,
  readOnly,
  onResolve,
}: ProductionSitePromptProps) => {
  const { t } = useTranslation()

  const { data, hasChange, onChange } = useForm<ProductionSiteState>({
    site_id: productionSite?.site_id ?? "",
    name: productionSite?.name ?? "",
    date_mise_en_service: productionSite?.date_mise_en_service ?? "",
    ges_option: productionSite?.ges_option ?? GESOption.Default,

    eligible_dc: productionSite?.eligible_dc ?? false,
    dc_reference: productionSite?.dc_reference ?? "",

    city: productionSite?.city ?? "",
    postal_code: productionSite?.postal_code ?? "",
    country: productionSite?.country ?? null,

    manager_name: productionSite?.manager_name ?? "",
    manager_phone: productionSite?.manager_phone ?? "",
    manager_email: productionSite?.manager_email ?? "",

    matieres_premieres: productionSite?.inputs ?? [],
    biocarburants: productionSite?.outputs ?? [],

    certificates: productionSite?.certificates ?? [],
  })

  const gesOptions = [
    { value: GESOption.Default, label: t("Valeurs par défaut") },
    { value: GESOption.NUTS2, label: t("Valeurs NUTS2") },
    { value: GESOption.Actual, label: t("Valeurs réelles") },
  ]

  const canSave = Boolean(
    hasChange && data.country && data.date_mise_en_service && data.name
  )

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={title} />
      {description && <DialogText text={description} />}

      <SettingsForm>
        <hr />

        <LabelInput
          readOnly={readOnly}
          label={t("Nom du site")}
          name="name"
          value={data.name}
          onChange={onChange}
        />

        <Box row>
          <LabelInput
            readOnly={readOnly}
            label={t("N° d'identification (SIRET)")}
            name="site_id"
            value={data.site_id}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            type="date"
            label={t("Date de mise en service")}
            name="date_mise_en_service"
            value={data.date_mise_en_service}
            onChange={onChange}
          />
        </Box>

        <hr />

        <Box row>
          <LabelInput
            readOnly={readOnly}
            label={t("Ville")}
            name="city"
            value={data.city}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label={t("Code postal")}
            name="postal_code"
            value={data.postal_code}
            onChange={onChange}
          />
        </Box>

        <LabelAutoComplete
          readOnly={readOnly}
          label={t("Pays")}
          placeholder={t("Rechercher un pays...")}
          name="country"
          value={data.country}
          getValue={(c) => c?.code_pays ?? ""}
          getLabel={(c) => t(c.code_pays, { ns: "countries" })}
          getQuery={common.findCountries}
          onChange={onChange}
        />

        <hr />

        <LabelInput
          readOnly={readOnly}
          label={t("Nom du gérant")}
          name="manager_name"
          value={data.manager_name}
          onChange={onChange}
        />
        <Box row>
          <LabelInput
            readOnly={readOnly}
            label={t("N° de téléphone du gérant")}
            name="manager_phone"
            value={data.manager_phone}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label={t("Addresse email du gérant")}
            name="manager_email"
            value={data.manager_email}
            onChange={onChange}
          />
        </Box>

        <hr />

        <Box row>
          <LabelCheckbox
            disabled
            label={t("Éligible au double-comptage ?")}
            name="eligible_dc"
            defaultChecked={data.eligible_dc}
          />
          <LabelInput
            disabled
            label={t("Référence double-comptage")}
            name="dc_reference"
            value={data.dc_reference}
          />
        </Box>

        <hr />

        <Label label={t("Options GES")}>
          <RadioGroup
            readOnly={readOnly}
            row
            value={data.ges_option}
            name="ges_option"
            options={gesOptions}
            onChange={onChange}
          />
        </Label>

        <hr />

        <Label label={t("Matieres premieres")}>
          <MultiAutocomplete
            readOnly={readOnly}
            value={data.matieres_premieres}
            name="matieres_premieres"
            placeholder={t("Ajouter matières premières...")}
            getValue={(o) => o?.code ?? ""}
            getLabel={(o) => t(o.code, { ns: "feedstocks" })}
            minLength={0}
            getQuery={common.findMatieresPremieres}
            onChange={onChange}
          />
        </Label>
        <Label label={t("Biocarburants")}>
          <MultiAutocomplete
            readOnly={readOnly}
            value={data.biocarburants}
            name="biocarburants"
            placeholder={t("Ajouter biocarburants...")}
            getValue={(o) => o.code}
            getLabel={(o) => t(o.code, { ns: "biofuels" })}
            minLength={0}
            getQuery={common.findBiocarburants}
            onChange={onChange}
          />
        </Label>

        <hr />

        <Label label={t("Certificats (2BS, ISCC)")}>
          <MultiAutocomplete
            readOnly={readOnly}
            name="certificates"
            placeholder={t("Rechercher des certificats...")}
            value={data.certificates}
            getValue={(c) => c.certificate_id}
            getLabel={(c) => c.certificate_id + " - " + c.certificate_holder}
            minLength={0}
            getQuery={() =>
              getMyCertificates(entity!.id).then(
                (res) => res.data.data?.map((e) => e.certificate) ?? []
              )
            }
            queryArgs={[entity?.id]}
            onChange={onChange}
          />
        </Label>

        <hr />

        <DialogButtons>
          {!readOnly && (
            <Button
              level="primary"
              icon={Save}
              disabled={!canSave}
              onClick={() => data && onResolve(data)}
            >
              <Trans>Sauvegarder</Trans>
            </Button>
          )}
          <Button icon={Return} onClick={() => onResolve()}>
            <Trans>Retour</Trans>
          </Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

type ProductionSitesSettingsProps = {
  settings: ProductionSiteSettingsHook
}

const ProductionSitesSettings = ({
  settings,
}: ProductionSitesSettingsProps) => {
  const { t } = useTranslation()
  const rights = useRights()

  const canModify = rights.is(UserRole.Admin, UserRole.ReadWrite)

  const actions =
    canModify && settings.removeProductionSite
      ? Actions([
          {
            icon: Cross,
            title: t("Supprimer le site de production"),
            action: settings.removeProductionSite,
          },
        ])
      : arrow

  const columns: Column<ProductionSiteDetails>[] = [
    padding,
    {
      header: t("ID"),
      className: styles.settingsTableColumn,
      render: (ps) => <Line text={`${ps.site_id}`} />,
    },
    {
      header: t("Nom"),
      className: styles.settingsTableColumn,
      render: (ps) => <Line text={ps.name} />,
    },
    {
      header: t("Pays"),
      className: styles.settingsTableColumn,
      render: (ps) => (
        <Line text={t(ps.country?.code_pays, { ns: "countries" })} />
      ),
    },
    {
      header: t("Date de mise en service"),
      className: styles.settingsTableColumn,
      render: (ps) => <Line text={formatDate(ps.date_mise_en_service)} />,
    },
    actions,
  ]

  const rows: Row<ProductionSiteDetails>[] = settings.productionSites.map(
    (ps) => ({
      value: ps,
      onClick: () => settings.editProductionSite(ps),
    })
  )

  return (
    <Section id="production">
      <SectionHeader>
        <Title>
          <Trans>Sites de production</Trans>
        </Title>
        {canModify && settings.createProductionSite && (
          <Button
            level="primary"
            icon={Plus}
            onClick={settings.createProductionSite}
          >
            <Trans>Ajouter un site de production</Trans>
          </Button>
        )}
      </SectionHeader>

      {settings.isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            <Trans>Aucun site de production trouvé</Trans>
          </Alert>
        </SectionBody>
      )}

      {!settings.isEmpty && (
        <Table columns={columns} rows={rows} className={styles.settingsTable} />
      )}

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default ProductionSitesSettings
