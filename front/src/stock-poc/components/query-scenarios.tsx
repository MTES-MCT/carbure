import { getQueryScenarios } from "../api"
import { Action } from "../types"
import { QueryScenarioTable } from "./query-scenario-table"
import { SelectDsfr } from "common/components/selects2"
import { Grid, Row } from "common/components/scaffold"
import { Text } from "common/components/text"
import useEntity from "common/hooks/entity"
import { useQuery } from "common/hooks/async"
import { useMemo, useState } from "react"
import { useTranslation } from "react-i18next"

type EntityOption = {
  id: number
  name: string
}

type QueryScenariosProps = {
  actions: Action[]
}

export const QueryScenarios = ({ actions }: QueryScenariosProps) => {
  const { t } = useTranslation()
  const authEntity = useEntity()

  const entityOptions = useMemo(() => {
    const byId = new Map<number, EntityOption>([
      [authEntity.id, { id: authEntity.id, name: authEntity.name }],
    ])
    for (const action of actions) {
      if (!byId.has(action.owner)) {
        byId.set(action.owner, { id: action.owner, name: action.owner_name })
      }
    }
    return [...byId.values()].sort((a, b) => a.name.localeCompare(b.name))
  }, [actions, authEntity.id, authEntity.name])

  const [queryEntityId, setQueryEntityId] = useState(authEntity.id)

  const queries = useQuery(getQueryScenarios, {
    key: "stock-poc-queries",
    params: [authEntity.id, queryEntityId],
  })

  const selectedEntityName =
    entityOptions.find((entity) => entity.id === queryEntityId)?.name ??
    `#${queryEntityId}`

  return (
    <div>
      <Row gap="md" style={{ alignItems: "flex-end", flexWrap: "wrap" }}>
        <Text is="h2" size="lg" fontWeight="bold">
          {t("Requêtes métier")}
        </Text>
        <Row gap="sm" style={{ marginLeft: "auto", alignItems: "flex-end" }}>
          <SelectDsfr
            label={t("Entité des requêtes")}
            value={String(queryEntityId)}
            onChange={(value) => setQueryEntityId(Number(value))}
            options={entityOptions.map((entity) => ({
              value: String(entity.id),
              label: entity.name,
            }))}
          />
        </Row>
      </Row>

      <Text size="sm" className="fr-text--mention">
        {t("Résultats pour {{name}}", { name: selectedEntityName })}
      </Text>

      <Grid cols={1}>
        {(queries.result?.scenarios ?? []).map((scenario) => (
          <div key={scenario.name} style={{ marginTop: "1.5rem" }}>
            <Text is="h3" size="md" fontWeight="bold">
              {scenario.name}
            </Text>
            <Text size="sm">{scenario.help}</Text>
            <QueryScenarioTable
              rows={scenario.results}
              loading={queries.loading}
            />
          </div>
        ))}
      </Grid>
    </div>
  )
}
