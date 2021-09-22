import { Fragment, useState } from "react"
import cl from "clsx"
import * as api from "../api"
import styles from "./entity-list.module.css"
import { padding } from "transactions/components/list-columns"
import Table, { Column } from "common/components/table"
import { useRelativePush } from "common/components/relative-route"
import { AlertFilter } from "common/components/alert"
import { AlertCircle } from "common/components/icons"

const COLUMNS: Column<api.EntityDetails>[] = [
  padding,
  { header: "Société", render: (e) => e.entity.name },
  {
    header: "Activité",
    render: (e) => e.entity.entity_type,
  },
]

type EntityListProps = {
  entities: api.EntityDetails[]
}

export const EntityFactoriesList = ({ entities }: EntityListProps) => {
  const push = useRelativePush()

  const columns: Column<api.EntityDetails>[] = [
    ...COLUMNS,
    {
      header: "Production",
      render: (e) => <span>{e.production_sites} sites de production</span>,
    },
    {
      header: "Stockage",
      render: (e) => <span>{e.depots} dépôts</span>,
    },
  ]

  const rows = entities
    .filter((e) => e.depots + e.production_sites > 0)
    .map((e) => ({
      value: e,
      onClick: () => push(`${e.entity.id}`),
    }))

  return <Table columns={columns} rows={rows} />
}

export const EntityDoubleCountingList = ({ entities }: EntityListProps) => {
  const push = useRelativePush()
  const [requestOnly, setRequestOnly] = useState(false)

  const requestCount =
    entities.filter((e) => e.double_counting_requests > 0).length ?? 0

  const columns: Column<api.EntityDetails>[] = [
    ...COLUMNS,
    {
      header: "Double comptage",
      render: (e) => (
        <ul className={styles.tableList}>
          <li
            className={cl(
              e.double_counting_requests > 0 && styles.entityRequestsCount
            )}
          >
            {e.double_counting_requests} dossiers en attente
          </li>
          <li>{e.double_counting} dossiers validés</li>
        </ul>
      ),
    },
  ]

  const rows = entities
    .filter((e) =>
      requestOnly
        ? e.double_counting_requests > 0
        : e.double_counting + e.double_counting_requests > 0
    )
    .map((e) => ({
      value: e,
      onClick: () => push(`${e.entity.id}`),
      className: cl(e.double_counting_requests > 0 && styles.entityRequests),
    }))

  return (
    <Fragment>
      {requestCount > 0 && (
        <AlertFilter
          level="warning"
          icon={AlertCircle}
          active={requestOnly}
          onActivate={() => setRequestOnly(true)}
          onDispose={() => setRequestOnly(false)}
        >
          <span>
            <b>{requestCount} sociétés</b> ont des dossiers double comptage en
            attente de validation
          </span>
        </AlertFilter>
      )}

      <Table columns={columns} rows={rows} />
    </Fragment>
  )
}

export const EntityCertificatesList = ({ entities }: EntityListProps) => {
  const push = useRelativePush()

  const columns: Column<api.EntityDetails>[] = [
    ...COLUMNS,
    {
      header: "ISCC",
      render: (e) => <span>{e.iscc} ISCC</span>,
    },
    {
      header: "2BS",
      render: (e) => <span>{e.dbs} 2BS</span>,
    },
    {
      header: "REDcert",
      render: (e) => <span>{e.redcert} REDcert</span>,
    },
    {
      header: "SN",
      render: (e) => <span>{e.sn} SN</span>,
    },
  ]

  const rows = entities
    .filter((e) => e.iscc + e.dbs + e.redcert + e.sn > 0)
    .map((e) => ({
      value: e,
      onClick: () => push(`${e.entity.id}`),
    }))

  return <Table columns={columns} rows={rows} />
}

export const EntityUsersList = ({ entities }: EntityListProps) => {
  const push = useRelativePush()
  const [requestOnly, setRequestOnly] = useState(false)

  const requestCount = entities.filter((e) => e.requests > 0).length ?? 0

  const columns: Column<api.EntityDetails>[] = [
    ...COLUMNS,
    {
      header: "Utilisateurs",
      render: (e) => (
        <ul className={styles.tableList}>
          <li className={cl(e.requests > 0 && styles.entityRequestsCount)}>
            {e.requests === 1
              ? `1 demande d'accès`
              : `${e.requests} demandes d'accès`}
          </li>
          <li>{e.users === 1 ? `1 utilisateur` : `${e.users} utilisateurs`}</li>
        </ul>
      ),
    },
  ]

  const rows = entities
    .filter((e) => (requestOnly ? e.requests > 0 : e.users + e.requests > 0))
    .map((e) => ({
      value: e,
      onClick: () => push(`${e.entity.id}`),
      className: cl(e.requests > 0 && styles.entityRequests),
    }))

  return (
    <Fragment>
      {requestCount > 0 && (
        <AlertFilter
          level="warning"
          icon={AlertCircle}
          active={requestOnly}
          onActivate={() => setRequestOnly(true)}
          onDispose={() => setRequestOnly(false)}
        >
          {requestCount === 1 ? (
            <span>
              <b>1 société</b> a des utilisateurs en attente d'autorisation.
            </span>
          ) : (
            <span>
              <b>{requestCount} sociétés</b> ont des utilisateurs en attente
              d'autorisation.
            </span>
          )}
        </AlertFilter>
      )}

      <Table columns={columns} rows={rows} />
    </Fragment>
  )
}
