import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"
import { Country, DeliverySite } from "../../services/types"

import styles from "./settings.module.css"

import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"

import { Title, Button, LabelInput, Box } from "../system"
import { AlertCircle, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Column, Row } from "../system/table"
import {
  SectionHeader,
  SectionForm,
  SectionBody,
  Section,
} from "../system/section"
import { prompt, PromptFormProps } from "../system/dialog"
import useForm from "../../hooks/helpers/use-form"
import AutoComplete from "../system/autocomplete"

type DeliverySiteState = {
  name: string
  city: string
  country: Country | null
  depot_id: string
  depot_type: "EFS" | "EPPE" | "OTHER" | ""
}

const DeliverySitePrompt = ({
  onConfirm,
  onCancel,
}: PromptFormProps<DeliverySiteState>) => {
  const [deliverySite, _, onChange] = useForm<DeliverySiteState>({
    name: "",
    city: "",
    country: null,
    depot_id: "",
    depot_type: "",
  })

  const canSave = Boolean(
    deliverySite.country &&
      deliverySite.city &&
      deliverySite.name &&
      deliverySite.depot_id &&
      deliverySite.depot_type
  )

  return (
    <Box as="form">
      <LabelInput label="Nom du site" name="name" onChange={onChange} />
      <LabelInput label="ID de douane" name="depot_id" onChange={onChange} />
      <LabelInput label="Type de dépôt" name="depot_type" onChange={onChange} />
      <LabelInput label="Ville" name="city" onChange={onChange} />

      <AutoComplete
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
  {
    className: styles.settingsTableEmptyColumn,
    render: () => null,
  },
  {
    header: "N° douane",
    className: styles.settingsTableIDColumn,
    render: (ds) => <span>{ds.depot_id}</span>,
  },
  {
    header: "Nom",
    className: styles.settingsTableColumn,
    render: (ds) => <span>{ds.name}</span>,
  },
  {
    header: "Ville",
    className: styles.settingsTableColumn,
    render: (ds) => <span>{ds.city}</span>,
  },
  {
    header: "Pays",
    className: styles.settingsTableColumn,
    render: (ds) => <span>{ds.country.name}</span>,
  },
]
type DeliverySitesSettingsProps = {
  entity: EntitySelection
}

const DeliverySitesSettings = ({ entity }: DeliverySitesSettingsProps) => {
  const [query, setQuery] = useState("")
  const [requestGetDeliverySites, resolveGetDeliverySites] = useAPI(common.findDeliverySites); // prettier-ignore

  const entityID = entity?.id
  const deliverySites = requestGetDeliverySites.data ?? []
  const isEmpty = query.length === 0 || deliverySites.length === 0

  async function createDeliverySite() {
    const data = await prompt(
      "Ajouter un site de livraison",
      "Veuillez entrer les informations de votre nouveau site de livraison.",
      DeliverySitePrompt
    )

    // @TODO actually add the certificate
  }

  const rows: Row<DeliverySite>[] = deliverySites.map((ds) => ({ value: ds }))

  useEffect(() => {
    if (query) {
      resolveGetDeliverySites(query)
    }
  }, [query])

  return (
    <Section>
      <SectionHeader>
        <Title>Sites de livraison</Title>
        <Button level="primary" icon={Plus} onClick={createDeliverySite}>
          Ajouter un site de livraison
        </Button>
      </SectionHeader>

      <SectionForm>
        <LabelInput
          label="Vérifier l'existence d'un site de livraison"
          placeholder="Rechercher sur Carbure..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
      </SectionForm>

      {isEmpty && (
        <SectionBody>
          <Alert icon={AlertCircle} level="warning">
            Aucun site de livraison trouvé
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
    </Section>
  )
}

export default DeliverySitesSettings
