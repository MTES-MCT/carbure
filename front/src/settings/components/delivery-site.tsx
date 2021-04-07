import React from "react"

import { Country, DepotType, OwnershipType, EntityType } from "common/types"
import {
  DeliverySiteSettingsHook,
  EntityDeliverySite,
} from "../hooks/use-delivery-sites"

import styles from "./settings.module.css"

import * as common from "common/api"

import { Title, Box, LoaderOverlay } from "common/components"
import { LabelInput, Label, LabelCheckbox } from "common/components/input"
import { Button } from "common/components/button"
import { AlertCircle, Cross, Plus, Return } from "common/components/icons"
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
import { LabelAutoComplete } from "common/components/autocomplete"
import { padding } from "transactions/components/list-columns"
import RadioGroup from "common/components/radio-group"
import { SettingsForm } from "./common"
import useForm from "common/hooks/use-form"
import { EntitySelection } from "carbure/hooks/use-entity"

const DEPOT_TYPE_LABELS = {
  [DepotType.EFS]: "EFS",
  [DepotType.EFPE]: "EFPE",
  [DepotType.Other]: "Autre",
  [DepotType.BiofuelDepot]: "Biofuel Depot",
  [DepotType.OilDepot]: "Oil Depot",
}

const OWNERSHIP_LABELS = {
  [OwnershipType.Own]: "Propre",
  [OwnershipType.ThirdParty]: "Tiers",
  [OwnershipType.Processing]: "Processing",
}

// prettier-ignore
const DEPOT_TYPES = Object.entries(DEPOT_TYPE_LABELS)
  .map(([value, label]) => ({ value, label }))

// prettier-ignore
const OWNERSHIP_TYPES = Object.entries(OWNERSHIP_LABELS)
  .map(([value, label]) => ({ value, label }))

type DeliverySiteFinderPromptProps = PromptProps<EntityDeliverySite> & {
  entity: EntitySelection
}

export const DeliverySiteFinderPrompt = ({
  entity,
  onResolve,
}: DeliverySiteFinderPromptProps) => {
  const { data, hasChange, onChange } = useForm<EntityDeliverySite>({
    depot: null,
    ownership_type: OwnershipType.ThirdParty,
    blending_is_outsourced: false,
    blender: null,
  })

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text="Ajouter dépôt" />
      <DialogText text="Veuillez rechercher un dépôt que vous utilisez." />

      <SettingsForm>
        <LabelAutoComplete
          label="Dépôt"
          placeholder="Rechercher un dépôt..."
          name="depot"
          value={data.depot}
          getQuery={common.findDeliverySites}
          onChange={onChange}
          getValue={(d) => d.depot_id}
          getLabel={(d) => d.name}
          queryArgs={[entity?.id]}
        />

        <Label label="Propriété">
          <RadioGroup
            row
            value={data.ownership_type}
            name="ownership_type"
            options={OWNERSHIP_TYPES}
            onChange={onChange}
          />
        </Label>

        {entity && entity.entity_type === EntityType.Operator && (
          <LabelCheckbox
            name="blending_is_outsourced"
            label="Incorporation potentiellement effectuée par un tiers"
            checked={data.blending_is_outsourced}
            onChange={onChange}
          />
        )}
        {data.blending_is_outsourced && (
          <LabelAutoComplete
            label="Incorporateur Tiers"
            placeholder="Rechercher un opérateur pétrolier..."
            name="blender"
            value={data.blender}
            getQuery={common.findOperators}
            onChange={onChange}
            getValue={(c) => c.id.toString()}
            getLabel={(c) => c.name}
          />
        )}

        <a
          href="mailto:carbure@beta.gouv.fr"
          target="_blank"
          rel="noreferrer"
          className={styles.settingsLink}
        >
          Le dépôt que je recherche n'est pas enregistré sur CarbuRe.
        </a>

        <DialogButtons>
          <Button
            level="primary"
            icon={Plus}
            disabled={!hasChange}
            onClick={() => onResolve(data)}
          >
            Ajouter
          </Button>
          <Button onClick={() => onResolve()}>Annuler</Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

type DeliverySiteState = {
  name: string
  city: string
  country: Country | null
  depot_id: string
  depot_type: DepotType
  address: string
  postal_code: string
  ownership_type: OwnershipType
  blending_is_outsourced: boolean
  blender: string
}

type DeliverySitePromptProps = PromptProps<EntityDeliverySite> & {
  title: string
  description?: string
  deliverySite?: EntityDeliverySite
}

export const DeliverySitePrompt = ({
  title,
  description,
  deliverySite,
  onResolve,
}: DeliverySitePromptProps) => {
  const form: DeliverySiteState = {
    name: deliverySite?.depot?.name ?? "",
    city: deliverySite?.depot?.city ?? "",
    country: deliverySite?.depot?.country ?? null,
    depot_id: deliverySite?.depot?.depot_id ?? "",
    depot_type: deliverySite?.depot?.depot_type ?? DepotType.Other,
    address: deliverySite?.depot?.address ?? "",
    postal_code: deliverySite?.depot?.postal_code ?? "",
    ownership_type: deliverySite?.ownership_type ?? OwnershipType.Own,
    blending_is_outsourced: deliverySite?.blending_is_outsourced ?? false,
    blender: deliverySite?.blender?.name ?? "",
  }

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text={title} />
      {description && <DialogText text={description} />}

      <SettingsForm>
        <hr />

        <Label label="Propriété">
          <RadioGroup
            row
            readOnly
            value={form.ownership_type}
            name="ownership_type"
            options={OWNERSHIP_TYPES}
          />
        </Label>

        <hr />

        <Label label="Incorporation tierce">
          <LabelCheckbox
            disabled
            label="L'incorporation est effectuée par un tiers"
            name="blending_is_outsourced"
            defaultChecked={form.blending_is_outsourced}
          />
          <LabelInput
            readOnly
            label="Incorporateur"
            name="blender"
            value={form.blender}
          />
        </Label>
        <hr />

        <LabelInput
          readOnly
          label="Nom du site"
          name="name"
          value={form.name}
        />
        <LabelInput
          readOnly
          label="ID de douane"
          name="depot_id"
          value={form.depot_id}
        />

        <hr />

        <Label label="Type de dépôt">
          <RadioGroup
            row
            readOnly
            value={form.depot_type}
            name="depot_type"
            options={DEPOT_TYPES}
          />
        </Label>

        <hr />

        <LabelInput
          readOnly
          label="Adresse"
          name="address"
          value={form.address}
        />

        <Box row>
          <LabelInput readOnly label="Ville" name="city" value={form.city} />
          <LabelInput
            readOnly
            label="Code postal"
            name="postal_code"
            value={form.postal_code}
          />
        </Box>

        <LabelInput
          readOnly
          label="Pays"
          placeholder="Rechercher un pays..."
          name="country"
          value={form.country?.name}
        />

        <hr />

        <DialogButtons>
          <Button icon={Return} onClick={() => onResolve()}>
            Retour
          </Button>
        </DialogButtons>
      </SettingsForm>
    </Dialog>
  )
}

const DELIVERY_SITE_COLUMNS: Column<EntityDeliverySite>[] = [
  padding,
  {
    header: "ID",
    render: (ds) => <Line text={ds.depot!.depot_id} />,
  },
  {
    header: "Nom",
    className: styles.settingsTableColumn,
    render: (ds) => <Line text={ds.depot!.name} />,
  },
  {
    header: "Type",
    render: (ds) => <Line text={DEPOT_TYPE_LABELS[ds.depot!.depot_type]} />,
  },
  {
    header: "Ville",
    className: styles.settingsTableColumn,
    render: (ds) => (
      <Line text={`${ds.depot!.city}, ${ds.depot!.country.name}`} />
    ),
  },
]

type DeliverySitesSettingsProps = {
  settings: DeliverySiteSettingsHook
}

const DeliverySitesSettings = ({ settings }: DeliverySitesSettingsProps) => {
  const actions = settings.deleteDeliverySite
    ? Actions([
        {
          icon: Cross,
          title: "Supprimer le dépôt",
          action: (ds: EntityDeliverySite) => settings.deleteDeliverySite!(ds),
        },
      ])
    : arrow

  const columns: Column<EntityDeliverySite>[] = [
    ...DELIVERY_SITE_COLUMNS,
    actions,
  ]

  const rows: Row<EntityDeliverySite>[] = settings.deliverySites.map((ds) => ({
    value: ds,
    onClick: () => settings.showDeliverySite(ds),
  }))

  return (
    <Section id="depot">
      <SectionHeader>
        <Title>Dépôts</Title>
        {settings.addDeliverySite && (
          <Button
            level="primary"
            icon={Plus}
            onClick={settings.addDeliverySite}
          >
            Ajouter un dépôt
          </Button>
        )}
      </SectionHeader>

      {settings.isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun dépôt trouvé
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

export default DeliverySitesSettings
