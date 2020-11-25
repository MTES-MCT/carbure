import React from "react"

import {
  Biocarburant,
  Certificate,
  Country,
  GESOption,
  MatierePremiere,
  ProductionSiteDetails,
} from "../../services/types"

import { ProductionSiteSettingsHook } from "../../hooks/settings/use-production-sites"
import { EntitySelection } from "../../hooks/helpers/use-entity"

import styles from "./settings.module.css"

import * as common from "../../services/common"
import useForm from "../../hooks/helpers/use-form"

import {
  Title,
  Box,
  Button,
  LabelInput,
  LoaderOverlay,
  Label,
  LabelCheckbox,
} from "../system"
import { AlertCircle, Cross, Plus, Save } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Actions, Column, Line, Row } from "../system/table"
import { SectionHeader, SectionBody, Section } from "../system/section"
import { DialogButtons, PromptFormProps } from "../system/dialog"
import { LabelAutoComplete, MultiAutocomplete } from "../system/autocomplete"
import RadioGroup from "../system/radio-group"
import { EMPTY_COLUMN, formatDate, SettingsForm } from "."
import { findCertificates } from "../../services/settings"

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

const GES_OPTIONS = [
  { value: GESOption.Default, label: "Valeurs par défaut" },
  { value: GESOption.NUTS2, label: "Valeurs NUTS2" },
  { value: GESOption.Actual, label: "Valeurs réelles" },
]

type ProductionSitePromptProps = PromptFormProps<ProductionSiteState>

// ville/code postal/addresse/pays numéro d'identification (SIRET), nom/prénom/téléphone/mail du gérant

export const ProductionSitePromptFactory = (
  entity: EntitySelection,
  productionSite?: ProductionSiteDetails
) =>
  function ProductionSitePrompt({
    onConfirm,
    onCancel,
  }: ProductionSitePromptProps) {
    const [form, hasChanged, onChange] = useForm<ProductionSiteState>({
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

    const canSave = Boolean(
      hasChanged && form.country && form.date_mise_en_service && form.name
    )

    return (
      <SettingsForm>
        <hr />

        <LabelInput
          label="Nom du site"
          name="name"
          value={form.name}
          onChange={onChange}
        />

        <Box row>
          <LabelInput
            label="N° d'identification (SIRET)"
            name="site_id"
            value={form.site_id}
            onChange={onChange}
          />
          <LabelInput
            type="date"
            label="Date de mise en service"
            name="date_mise_en_service"
            value={form.date_mise_en_service}
            onChange={onChange}
          />
        </Box>

        <hr />

        <Box row>
          <LabelInput
            label="Ville"
            name="city"
            value={form.city}
            onChange={onChange}
          />
          <LabelInput
            label="Code postal"
            name="postal_code"
            value={form.postal_code}
            onChange={onChange}
          />
        </Box>

        <LabelAutoComplete
          label="Pays"
          placeholder="Rechercher un pays..."
          name="country"
          value={form.country}
          getValue={(c) => c?.code_pays ?? ""}
          getLabel={(c) => c?.name ?? ""}
          getQuery={common.findCountries}
          onChange={onChange}
        />

        <hr />

        <LabelInput
          label="Nom du gérant"
          name="manager_name"
          value={form.manager_name}
          onChange={onChange}
        />
        <Box row>
          <LabelInput
            label="N° de téléphone du gérant"
            name="manager_phone"
            value={form.manager_phone}
            onChange={onChange}
          />
          <LabelInput
            label="Addresse email du gérant"
            name="manager_email"
            value={form.manager_email}
            onChange={onChange}
          />
        </Box>

        <hr />

        <Box row>
          <LabelCheckbox
            disabled
            label="Éligible au double-comptage ?"
            name="eligible_dc"
            defaultChecked={form.eligible_dc}
          />
          <LabelInput
            disabled
            label="Référence double-comptage"
            name="dc_reference"
            defaultValue={form.dc_reference}
          />
        </Box>

        <hr />

        <Label label="Options GES">
          <RadioGroup
            row
            value={form.ges_option}
            name="ges_option"
            options={GES_OPTIONS}
            onChange={onChange}
          />
        </Label>

        <hr />

        <Label label="Matieres premieres">
          <MultiAutocomplete
            value={form.matieres_premieres}
            name="matieres_premieres"
            placeholder="Ajouter matières premières..."
            getValue={(o) => o?.code ?? ""}
            getLabel={(o) => o?.name ?? ""}
            minLength={0}
            getQuery={common.findMatieresPremieres}
            onChange={onChange}
          />
        </Label>
        <Label label="Biocarburants">
          <MultiAutocomplete
            value={form.biocarburants}
            name="biocarburants"
            placeholder="Ajouter biocarburants..."
            getValue={(o) => o.code}
            getLabel={(o) => o.name}
            minLength={0}
            getQuery={common.findBiocarburants}
            onChange={onChange}
          />
        </Label>

        <hr />

        <Label label="Certificats (2BS, ISCC)">
          <MultiAutocomplete
            name="certificates"
            placeholder="Rechercher des certificats..."
            value={form.certificates}
            getValue={(c) => c.certificate_id}
            getLabel={(c) => c.certificate_id + " - " + c.holder}
            minLength={0}
            getQuery={findCertificates}
            queryArgs={[entity?.id]}
            onChange={onChange}
          />
        </Label>

        <hr />

        <DialogButtons>
          <Button
            level="primary"
            icon={Save}
            disabled={!canSave}
            onClick={() => form && onConfirm(form)}
          >
            Sauvegarder
          </Button>
          <Button onClick={onCancel}>Annuler</Button>
        </DialogButtons>
      </SettingsForm>
    )
  }

const PRODUCTION_SITE_COLUMNS: Column<ProductionSiteDetails>[] = [
  EMPTY_COLUMN,
  {
    header: "Nom",
    className: styles.settingsTableColumn,
    render: (ps) => <Line text={ps.name} />,
  },
  {
    header: "Pays",
    className: styles.settingsTableColumn,
    render: (ps) => <Line text={ps.country?.name} />,
  },
  {
    header: "Date de mise en service",
    className: styles.settingsTableColumn,
    render: (ps) => <Line text={formatDate(ps.date_mise_en_service)} />,
  },
]

type ProductionSitesSettingsProps = {
  settings: ProductionSiteSettingsHook
}

const ProductionSitesSettings = ({
  settings,
}: ProductionSitesSettingsProps) => {
  const columns = [
    ...PRODUCTION_SITE_COLUMNS,
    Actions([
      {
        icon: Cross,
        title: "Supprimer le site de production",
        action: settings.removeProductionSite,
      },
    ]),
  ]

  const rows: Row<ProductionSiteDetails>[] = settings.productionSites.map(
    (ps) => ({
      value: ps,
      onClick: () => settings.editProductionSite(ps),
    })
  )

  return (
    <Section>
      <SectionHeader>
        <Title>Sites de production</Title>
        <Button
          level="primary"
          icon={Plus}
          onClick={settings.createProductionSite}
        >
          Ajouter un site de production
        </Button>
      </SectionHeader>

      {settings.isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun site de production trouvé
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
