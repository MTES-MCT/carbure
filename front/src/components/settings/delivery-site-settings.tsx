import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"
import { Country, DeliverySite } from "../../services/types"

import styles from "./settings.module.css"

import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"

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
import { prompt, PromptFormProps } from "../system/dialog"
import useForm from "../../hooks/helpers/use-form"
import { LabelAutoComplete } from "../system/autocomplete"
import { EMPTY_COLUMN } from "."
import RadioGroup from "../system/radio-group"

const DEPOT_TYPES = [
  { label: "EFS", value: "EFS" },
  { label: "EPPE", value: "EPPE" },
  { label: "Autre", value: "OTHER" },
]

type DeliverySiteState = {
  name: string
  city: string
  country: Country | null
  depot_id: string
  depot_type: "EFS" | "EPPE" | "OTHER"
}

const DeliverySitePrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<DeliverySiteState>) => {
  const [deliverySite, hasChange, onChange] = useForm<DeliverySiteState>({
    name: "",
    city: "",
    country: null,
    depot_id: "",
    depot_type: "OTHER",
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
    <Box as="form">
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

      <Box row className={styles.dialogButtons}>
        <Button
          level="primary"
          icon={Plus}
          disabled={!canSave}
          onClick={() => deliverySite && onConfirm(deliverySite)}
        >
          Ajouter
        </Button>
        <Button onClick={onCancel}>Annuler</Button>
      </Box>
    </Box>
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
  entity: EntitySelection
}

const DeliverySitesSettings = ({ entity }: DeliverySitesSettingsProps) => {
  const [query, setQuery] = useState("")
  const [requestGetDeliverySites, resolveGetDeliverySites] = useAPI(common.findDeliverySites); // prettier-ignore
  const [requestAddDeliverySite, resolveAddDeliverySite] = useAPI(common.addDeliverySite); // prettier-ignore

  const entityID = entity?.id
  const deliverySites = requestGetDeliverySites.data ?? []

  const isLoading = requestGetDeliverySites.loading || requestAddDeliverySite.loading // prettier-ignore
  const isEmpty = deliverySites.length === 0 || query.length === 0

  async function createDeliverySite() {
    const data = await prompt(
      "Ajouter un dépôt",
      "Veuillez entrer les informations de votre nouveau dépôt.",
      DeliverySitePrompt
    )

    if (entityID && data && data.country) {
      resolveAddDeliverySite(
        data.name,
        data.city,
        data.country.code_pays,
        data.depot_id,
        data.depot_type
      ).then(() => setQuery(data.depot_id))
    }
  }

  const rows: Row<DeliverySite>[] = deliverySites.map((ds) => ({ value: ds }))

  useEffect(() => {
    if (query) {
      resolveGetDeliverySites(query)
    }
  }, [query, resolveGetDeliverySites])

  return (
    <Section>
      <SectionHeader>
        <Title>Dépôts</Title>
        <Button level="primary" icon={Plus} onClick={createDeliverySite}>
          Ajouter un dépôt
        </Button>
      </SectionHeader>

      <SectionForm>
        <LabelInput
          label="Vérifier l'existence d'un dépôt"
          placeholder="Rechercher sur Carbure..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </SectionForm>

      {query.length > 0 && isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun dépôt trouvé
          </Alert>
        </SectionBody>
      )}

      {!isEmpty && (
        <Table
          columns={DELIVERY_SITE_COLUMNS}
          rows={rows}
          className={styles.settingsTable}
        />
      )}

      {isLoading && <LoaderOverlay />}
    </Section>
  )
}

export default DeliverySitesSettings
