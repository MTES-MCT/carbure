import React from "react"

import {
  Country,
  DeliverySite,
  DepotType,
  OwnershipType,
} from "../../services/types"
import { DeliverySiteSettingsHook } from "../../hooks/settings/use-delivery-sites"

import styles from "./settings.module.css"

import * as common from "../../services/common"

import useForm from "../../hooks/helpers/use-form"
import { Title, Button, LabelInput, Box, LoaderOverlay, Label } from "../system"
import { AlertCircle, Plus, Return, Save } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Column, Line, Row } from "../system/table"
import {
  SectionHeader,
  SectionForm,
  SectionBody,
  Section,
} from "../system/section"
import { DialogButtons, PromptFormProps } from "../system/dialog"
import { LabelAutoComplete } from "../system/autocomplete"
import RadioGroup from "../system/radio-group"
import { EMPTY_COLUMN, SettingsForm } from "."

const DEPOT_TYPE_LABELS = {
  [DepotType.EFS]: "EFS",
  [DepotType.EFPE]: "EFPE",
  [DepotType.Other]: "Autre",
}

const OWNERSHIP_LABELS = {
  [OwnershipType.Own]: "Propre",
  [OwnershipType.ThirdParty]: "Tiers",
}

// prettier-ignore
const DEPOT_TYPES = Object.entries(DEPOT_TYPE_LABELS)
  .map(([value, label]) => ({ value, label }))

// prettier-ignore
const OWNERSHIP_TYPES = Object.entries(OWNERSHIP_LABELS)
  .map(([value, label]) => ({ value, label }))

type DeliverySiteState = {
  name: string
  city: string
  country: Country | null
  depot_id: string
  depot_type: DepotType
  address: string
  postal_code: string
  ownership_type: OwnershipType
}

export const DeliverySitePromptFactory = (
  deliverySite?: DeliverySite,
  readOnly?: boolean
) =>
  function DeliverySitePrompt({
    onConfirm,
    onCancel,
  }: PromptFormProps<DeliverySiteState>) {
    const [form, hasChange, onChange] = useForm<DeliverySiteState>({
      name: deliverySite?.name ?? "",
      city: deliverySite?.city ?? "",
      country: deliverySite?.country ?? null,
      depot_id: deliverySite?.depot_id ?? "",
      depot_type: deliverySite?.depot_type ?? DepotType.Other,
      address: deliverySite?.address ?? "",
      postal_code: deliverySite?.postal_code ?? "",
      ownership_type: deliverySite?.ownership_type ?? OwnershipType.Own,
    })

    const canSave = Boolean(
      hasChange &&
        form.country &&
        form.city &&
        form.name &&
        form.depot_id &&
        form.depot_type
    )

    return (
      <SettingsForm>
        <hr />

        <LabelInput
          readOnly={readOnly}
          label="Nom du site"
          name="name"
          value={form.name}
          onChange={onChange}
        />
        <LabelInput
          readOnly={readOnly}
          label="ID de douane"
          name="depot_id"
          value={form.depot_id}
          onChange={onChange}
        />

        <hr />

        <Label label="Type de dépôt">
          <RadioGroup
            row
            readOnly={readOnly}
            value={form.depot_type}
            name="depot_type"
            onChange={onChange}
            options={DEPOT_TYPES}
          />
        </Label>

        <hr />

        <LabelInput
          readOnly={readOnly}
          label="Adresse"
          name="address"
          value={form.address}
          onChange={onChange}
        />

        <Box row>
          <LabelInput
            readOnly={readOnly}
            label="Ville"
            name="city"
            value={form.city}
            onChange={onChange}
          />
          <LabelInput
            readOnly={readOnly}
            label="Code postal"
            name="postal_code"
            value={form.postal_code}
            onChange={onChange}
          />
        </Box>

        <LabelAutoComplete
          readOnly={readOnly}
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

        <Label label="Propriété">
          <RadioGroup
            row
            readOnly={readOnly}
            value={form.ownership_type}
            name="ownership_type"
            onChange={onChange}
            options={OWNERSHIP_TYPES}
          />
        </Label>

        <hr />

        <DialogButtons>
          {!readOnly && (
            <React.Fragment>
              <Button
                level="primary"
                icon={Save}
                disabled={!canSave}
                onClick={() => form && onConfirm(form)}
              >
                Sauvegarder
              </Button>
              <Button onClick={onCancel}>Annuler</Button>
            </React.Fragment>
          )}

          {readOnly && (
            <Button icon={Return} onClick={onCancel}>
              Retour
            </Button>
          )}
        </DialogButtons>
      </SettingsForm>
    )
  }

const DELIVERY_SITE_COLUMNS: Column<DeliverySite>[] = [
  EMPTY_COLUMN,
  {
    header: "N° douane",
    className: styles.settingsTableIDColumn,
    render: (ds) => <Line text={ds.depot_id} />,
  },
  {
    header: "Type",
    className: styles.settingsTableIDColumn,
    render: (ds) => <Line text={DEPOT_TYPE_LABELS[ds.depot_type]} />,
  },
  {
    header: "Nom",
    className: styles.settingsTableColumn,
    render: (ds) => <Line text={ds.name} />,
  },
  {
    header: "Ville",
    className: styles.settingsTableColumn,
    render: (ds) => <Line text={ds.city} />,
  },
  {
    header: "Pays",
    className: styles.settingsTableColumn,
    render: (ds) => <Line text={ds.country.name} />,
  },
]

type DeliverySitesSettingsProps = {
  settings: DeliverySiteSettingsHook
}

const DeliverySitesSettings = ({ settings }: DeliverySitesSettingsProps) => {
  const rows: Row<DeliverySite>[] = settings.deliverySites.map((ds) => ({
    value: ds,
    onClick: () => settings.showDeliverySite(ds),
  }))

  return (
    <Section>
      <SectionHeader>
        <Title>Dépôts</Title>
        <Button
          level="primary"
          icon={Plus}
          onClick={settings.createDeliverySite}
        >
          Ajouter un dépôt
        </Button>
      </SectionHeader>

      <SectionForm>
        <LabelInput
          label="Vérifier l'existence d'un dépôt"
          placeholder="Rechercher sur Carbure..."
          value={settings.query}
          onChange={(e) => settings.setQuery(e.target.value)}
        />
      </SectionForm>

      {settings.query.length > 0 && settings.isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun dépôt trouvé
          </Alert>
        </SectionBody>
      )}

      {!settings.isEmpty && (
        <Table
          columns={DELIVERY_SITE_COLUMNS}
          rows={rows}
          className={styles.settingsTable}
        />
      )}

      {settings.isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default DeliverySitesSettings
