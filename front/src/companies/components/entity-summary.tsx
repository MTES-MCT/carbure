import { useState } from "react"
import { useTranslation } from "react-i18next"
import cl from "clsx"
import * as api from "../api"
import { EntityDetails } from "companies/types"
import css from "./entity-summary.module.css"
import Table, { Cell } from "common/components/table"
import { Alert } from "common/components/alert"
import { AlertTriangle } from "common/components/icons"
import { Panel, LoaderOverlay, Grid } from "common/components/scaffold"
import { useQuery } from "common/hooks/async"
import { matchesSearch } from "common/utils/collection"
import MultiSelect from "common/components/multi-select"
import Select from "common/components/select"
import { EntityType } from "carbure/types"
import {
  getEntityTypeLabel,
  normalizeEntityType,
} from "common/utils/normalizers"

type EntitySummaryProps = {
  search?: string
}

type Operation = "user" | "certificate" | "double-counting"

export const EntitySummary = ({ search = "" }: EntitySummaryProps) => {
  const { t } = useTranslation()

  const entities = useQuery(api.getEntities, {
    key: "entities",
    params: [],
  })

  const [types, setTypes] = useState<EntityType[] | undefined>(undefined)
  const [operation, setOperations] = useState<Operation | undefined>(undefined)

  const entityData = entities.result?.data.data ?? []

  const matchedEntities = entityData.filter(
    (e) =>
      matchesSearch(search, [e.entity.name]) &&
      hasTypes(e, types) &&
      hasOperation(e, operation)
  )

  const hasResults = matchedEntities.length > 0

  return (
    <>
      <Grid>
        <MultiSelect
          clear
          value={types}
          onChange={setTypes}
          label={t("Types d'entité")}
          placeholder="Choisissez un ou plusieurs types"
          normalize={normalizeEntityType}
          options={[
            EntityType.Operator,
            EntityType.Producer,
            EntityType.Trader,
            EntityType.Auditor,
          ]}
        />
        <Select
          clear
          value={operation}
          onChange={setOperations}
          label={t("Opérations en attente")}
          placeholder="Choisissez une opération"
          options={[
            { value: "user", label: t("Utilisateurs à autoriser") },
            { value: "certificate", label: t("Certificats à valider") },
            { value: "double-counting", label: t("Dossiers double comptage") },
          ]}
        />
      </Grid>

      {!hasResults && (
        <Alert icon={AlertTriangle} variant="warning">
          Aucune société trouvée pour cette recherche.
        </Alert>
      )}

      {hasResults && (
        <Panel>
          <header>
            <h1>Récapitulatif des sociétés</h1>
          </header>
          <Table
            loading={entities.loading}
            rows={matchedEntities}
            rowLink={(e) => `${e.entity.id}`}
            columns={[
              {
                key: "entities",
                header: t("Société"),
                orderBy: (e) => e.entity.name,
                cell: (e) => (
                  <Cell
                    text={e.entity.name}
                    sub={getEntityTypeLabel(e.entity.entity_type)}
                  />
                ),
              },
              {
                key: "factories",
                header: t("Production / Stockage"),
                orderBy: (e) => e.production_sites + e.depots,
                cell: (e) => (
                  <EntityInfoCell
                    data={[
                      {
                        count: e.production_sites,
                        label: t("{{count}} site de production", { count: e.production_sites }), // prettier-ignore
                      },
                      {
                        count: e.depots,
                        label: t("{{count}} dépôts", { count: e.depots }), // prettier-ignore
                      },
                    ]}
                  />
                ),
              },
              {
                key: "certificates",
                header: t("Certificats"),
                orderBy: (e) => e.certificates,
                cell: (e) => (
                  <EntityInfoCell
                    data={[
                      {
                        count: e.certificates_pending,
                        label: t("{{count}} certificats à valider", { count: e.certificates_pending }), // prettier-ignore
                        highlight: true,
                      },
                      {
                        count: e.certificates,
                        label: t("{{count}} certificats", { count: e.certificates }), // prettier-ignore
                      },
                    ]}
                  />
                ),
              },
              {
                key: "double-counting",
                header: t("Double comptage"),
                orderBy: (e) => e.double_counting_requests * 1000 + e.double_counting, // prettier-ignore
                cell: (e) => (
                  <EntityInfoCell
                    data={[
                      {
                        count: e.double_counting_requests,
                        label: t("{{count}} dossier en attente", { count: e.double_counting_requests }), // prettier-ignore
                        highlight: true,
                      },
                      {
                        count: e.double_counting,
                        label: t("{{count}} dossier validé", { count: e.double_counting }), // prettier-ignore
                      },
                    ]}
                  />
                ),
              },
              {
                key: "users",
                header: t("Utilisateurs"),
                orderBy: (e) => e.requests * 1000 + e.users,
                cell: (e) => (
                  <EntityInfoCell
                    data={[
                      {
                        count: e.requests,
                        label: t("{{count}} demande d'accès", { count: e.requests }), // prettier-ignore
                        highlight: true,
                      },
                      {
                        count: e.users,
                        label: t("{{count}} utilisateur", { count: e.users }),
                      },
                    ]}
                  />
                ),
              },
            ]}
          />
          {entities.loading && <LoaderOverlay />}
        </Panel>
      )}
    </>
  )
}

interface EntityInfo {
  count: number
  label: string
  highlight?: Boolean
}

const EntityInfoCell = ({ data }: { data: EntityInfo[] }) => (
  <ul className={css.tableList}>
    {data.every((i) => !i.count) && "-"}
    {data.map(
      ({ count, label, highlight }, i) =>
        count > 0 && (
          <li key={i} className={cl(highlight && css.requestHighlight)}>
            {label}
          </li>
        )
    )}
  </ul>
)

function hasTypes(details: EntityDetails, types: EntityType[] | undefined) {
  if (types === undefined || types.length === 0) return true
  else return types.includes(details.entity.entity_type)
}

function hasOperation(
  details: EntityDetails,
  operation: Operation | undefined
) {
  if (operation === undefined) return true
  if (operation === "user" && details.requests > 0) return true
  if (operation === "certificate" && details.certificates_pending > 0) return true // prettier-ignore
  if (operation === "double-counting" && details.double_counting_requests > 0) return true // prettier-ignore
}
