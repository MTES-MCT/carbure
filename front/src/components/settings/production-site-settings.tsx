import React from "react"

import {
  Biocarburant,
  Country,
  MatierePremiere,
  ProductionSiteDetails,
} from "../../services/types"

import styles from "./settings.module.css"

import * as common from "../../services/common"
import useForm from "../../hooks/helpers/use-form"

import { Title, Box, Button, LabelInput, LoaderOverlay, Label } from "../system"
import { AlertCircle, Cross, Plus, Save } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Actions, Column, Line, Row } from "../system/table"

import { SectionHeader, SectionBody, Section } from "../system/section"
import { PromptFormProps } from "../system/dialog"
import { LabelAutoComplete, MultiAutocomplete } from "../system/autocomplete"
import { EMPTY_COLUMN } from "."
import { ProductionSiteSettingsHook } from "../../hooks/settings/use-production-sites"

export type ProductionSiteState = {
  name: string
  country: Country | null
  date_mise_en_service: string
  matieres_premieres: MatierePremiere[]
  biocarburants: Biocarburant[]
}

type ProductionSitePromptProps = PromptFormProps<ProductionSiteState> & {
  productionSite?: ProductionSiteDetails
}

export const ProductionSitePrompt = ({
  productionSite,
  onConfirm,
  onCancel,
}: ProductionSitePromptProps) => {
  const [form, hasChanged, onChange] = useForm<ProductionSiteState>({
    name: productionSite?.name ?? "",
    country: productionSite?.country ?? null,
    date_mise_en_service: productionSite?.date_mise_en_service ?? "",
    matieres_premieres: productionSite?.inputs ?? [],
    biocarburants: productionSite?.outputs ?? [],
  })

  const canSave = Boolean(
    hasChanged && form.country && form.date_mise_en_service && form.name
  )

  return (
    <Box as="form">
      <LabelInput
        label="Nom du site"
        name="name"
        value={form.name}
        onChange={onChange}
      />

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

      <LabelInput
        type="date"
        label="Date de mise en service"
        name="date_mise_en_service"
        value={form.date_mise_en_service}
        onChange={onChange}
      />

      <Label label="Matieres premieres">
        <MultiAutocomplete
          value={form.matieres_premieres}
          name="matieres_premieres"
          placeholder="Ajouter matières premières..."
          getValue={(o) => o.code}
          getLabel={(o) => o.name}
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
          getQuery={common.findBiocarburants}
          onChange={onChange}
        />
      </Label>

      <Box row className={styles.dialogButtons}>
        <Button
          level="primary"
          icon={Save}
          disabled={!canSave}
          onClick={() => form && onConfirm(form)}
        >
          Sauvegarder
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </Box>
    </Box>
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
    render: (ps) => <Line text={ps.date_mise_en_service} />,
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
