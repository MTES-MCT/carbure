import { Main, Title } from "common/components"
import { Alert } from "common/components/alert"
import { AlertTriangle } from "common/components/icons"
import { LabelInput } from "common/components/input"
import { useRelativePush } from "common/components/relative-route"
import Table, { Column } from "common/components/table"
import useAPI from "common/hooks/use-api"
import { useEffect, useState } from "react"
import { SettingsBody, SettingsHeader } from "settings/components/common"
import { empty } from "transactions/components/list-columns"

import * as api from "./api"

const COLUMNS: Column<api.EntityDetails>[] = [
  empty,
  { header: "Société", render: (e) => e.entity.name },
  { header: "Activité", render: (e) => e.entity.entity_type },
  {
    header: "Utilisateurs",
    render: (e) => (
      <ul style={{ padding: 0, margin: 0 }}>
        <li>{e.requests} demandes d'accès</li>
        <li>{e.users} autorisations</li>
      </ul>
    ),
  },
  {
    header: "Production/Stockage",
    render: (e) => (
      <ul style={{ padding: 0, margin: 0 }}>
        <li>{e.production_sites} sites de production</li>
        <li>{e.depots} dépôts</li>
      </ul>
    ),
  },
  {
    header: "Certificats",
    render: (e) => (
      <ul style={{ padding: 0, margin: 0 }}>
        <li>{e.certificates_iscc} certificats ISCC</li>
        <li>{e.certificates_2bs} certificats 2BS</li>
      </ul>
    ),
  },
]

const Entities = () => {
  const push = useRelativePush()
  const [query, setQuery] = useState("")
  const [entities, getEntities] = useAPI(api.getEntities)

  useEffect(() => {
    getEntities(query)
  }, [getEntities, query])

  const rows = (entities.data ?? []).map((e) => ({
    value: e,
    onClick: () => push(`${e.entity.id}`),
  }))

  return (
    <Main>
      <SettingsHeader>
        <Title>Sociétés</Title>
      </SettingsHeader>

      <SettingsBody>
        <LabelInput
          label="Rechercher..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        {rows.length === 0 && (
          <Alert icon={AlertTriangle} level="warning">
            Aucune société trouvée pour ces paramètres.
          </Alert>
        )}
        {rows.length > 0 && <Table columns={COLUMNS} rows={rows} />}
      </SettingsBody>
    </Main>
  )
}

export default Entities
