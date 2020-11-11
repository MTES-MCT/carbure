import React, { useEffect, useState } from "react"

import { EntitySelection } from "../../hooks/helpers/use-entity"
import { DeliverySite } from "../../services/types"

import styles from "./settings.module.css"

import * as common from "../../services/common"
import useAPI from "../../hooks/helpers/use-api"

import { Title, Button, LabelInput } from "../system"
import { AlertCircle, Plus } from "../system/icons"
import { Alert } from "../system/alert"
import Table, { Column, Row } from "../system/table"
import {
  SectionHeader,
  SectionForm,
  SectionBody,
  Section,
} from "../system/section"

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
        <Button level="primary" icon={Plus}>
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
