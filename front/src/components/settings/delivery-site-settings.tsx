import React from "react"

import { Country, DeliverySite, DepotType } from "../../services/types"
import { DeliverySiteSettingsHook } from "../../hooks/settings/use-delivery-sites"

import styles from "./settings.module.css"

import * as common from "../../services/common"

import useForm from "../../hooks/helpers/use-form"
import { Title, Button, LabelInput, Box, LoaderOverlay, Label } from "../system"
import { AlertCircle, Plus } from "../system/icons"
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

// prettier-ignore
const DEPOT_TYPES = Object.entries(DEPOT_TYPE_LABELS)
  .map(([value, label]) => ({ value, label }))

type DeliverySiteState = {
  name: string
  city: string
  country: Country | null
  depot_id: string
  depot_type: DepotType
}

export const DeliverySitePrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<DeliverySiteState>) => {
  const [deliverySite, hasChange, onChange] = useForm<DeliverySiteState>({
    name: "",
    city: "",
    country: null,
    depot_id: "",
    depot_type: DepotType.Other,
  })

  const canSave = Boolean(
    hasChange &&
      deliverySite.country &&
      deliverySite.city &&
      deliverySite.name &&
      deliverySite.depot_id &&
      deliverySite.depot_type
  )

  return (
    <SettingsForm>
      <Label label="Type de dépôt">
        <RadioGroup
          row
          value={deliverySite.depot_type}
          name="depot_type"
          onChange={onChange}
          options={DEPOT_TYPES}
        />
      </Label>

      <LabelInput
        label="Nom du site"
        name="name"
        value={deliverySite.name}
        onChange={onChange}
      />
      <LabelInput
        label="ID de douane"
        name="depot_id"
        value={deliverySite.depot_id}
        onChange={onChange}
      />
      <LabelInput
        label="Ville"
        name="city"
        value={deliverySite.city}
        onChange={onChange}
      />
      <LabelAutoComplete
        label="Pays"
        placeholder="Rechercher un pays..."
        name="country"
        value={deliverySite.country}
        getValue={(c) => c?.code_pays ?? ""}
        getLabel={(c) => c?.name ?? ""}
        getQuery={common.findCountries}
        onChange={onChange}
      />

      <DialogButtons>
        <Button
          level="primary"
          icon={Plus}
          disabled={!canSave}
          onClick={() => deliverySite && onConfirm(deliverySite)}
        >
          Ajouter
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
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
