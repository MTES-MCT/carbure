import React from "react"

import {
  Biocarburant,
  ProductionCertificate,
  Country,
  GESOption,
  MatierePremiere,
  ProductionSiteDetails,
} from "common/types"

import { ProductionSiteSettingsHook } from "../hooks/use-production-sites"
import { EntitySelection } from "carbure/hooks/use-entity"

import styles from "./settings.module.css"

import * as common from "common/api"
import useForm from "common/hooks/use-form"

import { Title, Box, LoaderOverlay } from "common/components"
import { LabelInput, Label, LabelCheckbox } from "common/components/input"
import { Button } from "common/components/button"
import { AlertCircle, Cross, Plus, Return, Save } from "common/components/icons"
import { Alert } from "common/components/alert"
import Table, {
  Actions,
  arrow,
  Column,
  Line,
  Row,
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
import { padding } from "transactions/components/list-columns"
import { findCertificates } from "../api"

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
  certificates: ProductionCertificate[]
}

const GES_OPTIONS = [
  { value: GESOption.Default, label: "Valeurs par défaut" },
  { value: GESOption.NUTS2, label: "Valeurs NUTS2" },
  { value: GESOption.Actual, label: "Valeurs réelles" },
]

type ProductionSitePromptProps = PromptProps<ProductionSiteState> & {
  title: string
  description?: string
  entity: EntitySelection
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
          label="Nom du site"
          name="name"
          value={data.name}
          onChange={onChange}
        />

        <Box row>
          <LabelInput
            readOnly={readOnly}
            label="N° d'identification (SIRET)"
            name="site_id"
            value={data.site_id}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            type="date"
            label="Date de mise en service"
            name="date_mise_en_service"
            value={data.date_mise_en_service}
            onChange={onChange}
          />
        </Box>

        <hr />

        <Box row>
          <LabelInput
            readOnly={readOnly}
            label="Ville"
            name="city"
            value={data.city}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Code postal"
            name="postal_code"
            value={data.postal_code}
            onChange={onChange}
          />
        </Box>

        <LabelAutoComplete
          readOnly={readOnly}
          label="Pays"
          placeholder="Rechercher un pays..."
          name="country"
          value={data.country}
          getValue={(c) => c?.code_pays ?? ""}
          getLabel={(c) => c?.name ?? ""}
          getQuery={common.findCountries}
          onChange={onChange}
        />

        <hr />

        <LabelInput
          readOnly={readOnly}
          label="Nom du gérant"
          name="manager_name"
          value={data.manager_name}
          onChange={onChange}
        />
        <Box row>
          <LabelInput
            readOnly={readOnly}
            label="N° de téléphone du gérant"
            name="manager_phone"
            value={data.manager_phone}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Addresse email du gérant"
            name="manager_email"
            value={data.manager_email}
            onChange={onChange}
          />
        </Box>

        <hr />

        <Box row>
          <LabelCheckbox
            disabled
            label="Éligible au double-comptage ?"
            name="eligible_dc"
            defaultChecked={data.eligible_dc}
          />
          <LabelInput
            disabled
            label="Référence double-comptage"
            name="dc_reference"
            value={data.dc_reference}
          />
        </Box>

        <hr />

        <Label label="Options GES">
          <RadioGroup
            readOnly={readOnly}
            row
            value={data.ges_option}
            name="ges_option"
            options={GES_OPTIONS}
            onChange={onChange}
          />
        </Label>

        <hr />

        <Label label="Matieres premieres">
          <MultiAutocomplete
            readOnly={readOnly}
            value={data.matieres_premieres}
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
            readOnly={readOnly}
            value={data.biocarburants}
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
            readOnly={readOnly}
            name="certificates"
            placeholder="Rechercher des certificats..."
            value={data.certificates}
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
          {!readOnly && (
            <Button
              level="primary"
              icon={Save}
              disabled={!canSave}
              onClick={() => data && onResolve(data)}
            >
              Sauvegarder
            </Button>
          )}
          <Button icon={Return} onClick={() => onResolve()}>
            Retour
          </Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

const PRODUCTION_SITE_COLUMNS: Column<ProductionSiteDetails>[] = [
  padding,
  {
    header: "ID",
    className: styles.settingsTableColumn,
    render: (ps) => <Line text={`${ps.site_id}`} />,
  },
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
  const actions = settings.removeProductionSite
    ? Actions([
        {
          icon: Cross,
          title: "Supprimer le site de production",
          action: settings.removeProductionSite,
        },
      ])
    : arrow

  const columns = [...PRODUCTION_SITE_COLUMNS, actions]

  const rows: Row<ProductionSiteDetails>[] = settings.productionSites.map(
    (ps) => ({
      value: ps,
      onClick: () => settings.editProductionSite(ps),
    })
  )

  return (
    <Section id="production">
      <SectionHeader>
        <Title>Sites de production</Title>
        {settings.createProductionSite && (
          <Button
            level="primary"
            icon={Plus}
            onClick={settings.createProductionSite}
          >
            Ajouter un site de production
          </Button>
        )}
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
