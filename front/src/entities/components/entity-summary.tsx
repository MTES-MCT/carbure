import { useNavigate } from "react-router-dom"
import cl from "clsx"
import * as api from "../api"
import css from "./entity-summary.module.css"
import Table, { Cell } from "common-v2/components/table"
import { Alert } from "common/components/alert"
import { AlertTriangle } from "common-v2/components/icons"
import { Panel, LoaderOverlay } from "common-v2/components/scaffold"
import { useTranslation } from "react-i18next"
import { useQuery } from "common-v2/hooks/async"
import { matchesSearch } from "common-v2/utils/collection"

type EntitySummaryProps = {
  search?: string
}

export const EntitySummary = ({ search = "" }: EntitySummaryProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()

  const entities = useQuery(api.getEntities, {
    key: "entities",
    params: [],
  })

  const entityData = (entities.result ?? []).filter((e) =>
    matchesSearch(search, [e.entity.name, e.entity.entity_type])
  )

  if (entityData.length === 0) {
    return (
      <Alert icon={AlertTriangle} level="warning">
        Aucune société trouvée pour cette recherche.
      </Alert>
    )
  }

  return (
    <Panel>
      <header>
        <h1>Récapitulatif des sociétés</h1>
      </header>
      <Table
        rows={entityData}
        onAction={(e) => navigate(`${e.entity.id}`)}
        columns={[
          {
            key: "entities",
            header: "Société",
            orderBy: (e) => e.entity.name,
            cell: (e) => (
              <Cell text={e.entity.name} sub={t(e.entity.entity_type)} />
            ),
          },
          {
            key: "factories",
            header: "Production / Stockage",
            orderBy: (e) => e.production_sites + e.depots,
            cell: (e) => (
              <ul>
                <li>{e.production_sites} sites de production</li>
                <li>{e.depots} dépôts</li>
              </ul>
            ),
          },
          {
            key: "certificates",
            header: "Certificats",
            orderBy: (e) => e.certificates,
            cell: (e) => (
              <ul>
                <li>{e.certificates} certificats</li>
              </ul>
            ),
          },
          {
            key: "double-counting",
            header: "Double comptage",
            orderBy: (e) =>
              e.double_counting_requests * 1000 + e.double_counting,
            cell: (e) => (
              <ul className={css.tableList}>
                <li
                  className={cl(
                    e.double_counting_requests > 0 && css.entityRequestsCount
                  )}
                >
                  {e.double_counting_requests} dossiers en attente
                </li>
                <li>{e.double_counting} dossiers validés</li>
              </ul>
            ),
          },
          {
            key: "users",
            header: "Utilisateurs",
            orderBy: (e) => e.requests * 1000 + e.users,
            cell: (e) => (
              <ul className={css.tableList}>
                <li className={cl(e.requests > 0 && css.entityRequestsCount)}>
                  {e.requests === 1
                    ? `1 demande d'accès`
                    : `${e.requests} demandes d'accès`}
                </li>
                <li>
                  {e.users === 1 ? `1 utilisateur` : `${e.users} utilisateurs`}
                </li>
              </ul>
            ),
          },
        ]}
      />
      {entities.loading && <LoaderOverlay />}
    </Panel>
  )
}
