import cl from "clsx"
import { padding } from "transactions/components/list-columns"
import * as api from "../api"
import Table, { Column } from "common/components/table"
import { useRelativePush } from "common/components/relative-route"

import styles from "./entity-list.module.css"

const COLUMNS: Column<api.EntityDetails>[] = [
  padding,
  { header: "Société", render: (e) => e.entity.name },
  { header: "Activité", render: (e) => e.entity.entity_type },
  {
    header: "Utilisateurs",
    render: (e) => (
      <ul style={{ fontWeight: "normal", padding: 0, margin: 0 }}>
        <li>{e.requests} demandes d'accès</li>
        <li>{e.users} autorisations</li>
      </ul>
    ),
  },
  {
    header: "Production/Stockage",
    render: (e) => (
      <ul style={{ fontWeight: "normal", padding: 0, margin: 0 }}>
        <li>{e.production_sites} sites de production</li>
        <li>{e.depots} dépôts</li>
      </ul>
    ),
  },
  {
    header: "Certificats",
    render: (e) => (
      <ul style={{ fontWeight: "normal", padding: 0, margin: 0 }}>
        <li>{e.certificates_iscc} certificats ISCC</li>
        <li>{e.certificates_2bs} certificats 2BS</li>
      </ul>
    ),
  },
]

type EntityListProps = {
  entities: api.EntityDetails[]
}

const EntityList = ({ entities }: EntityListProps) => {
  const push = useRelativePush()

  const rows = entities.map((e) => ({
    value: e,
    onClick: () => push(`${e.entity.id}`),
    className: cl(e.requests > 0 && styles.entityRequests),
  }))

  return <Table columns={COLUMNS} rows={rows} />
}

export default EntityList
