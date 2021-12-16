import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { EntityType } from "carbure/types"
import { useQuery } from "common-v2/hooks/async"
import { findEntities } from "common-v2/api"
import { Main } from "common-v2/components/scaffold"
import { SearchInput } from "common-v2/components/input"
import { Alert } from "common-v2/components/alert"
import { AlertCircle } from "common-v2/components/icons"
import Table from "common-v2/components/table"

const Registry = () => {
  const { t } = useTranslation()
  const [query, setQuery] = useState<string | undefined>("")

  const entities = useQuery(findEntities, {
    key: "entities",
    params: [query],
  })

  const entityTypes = {
    [EntityType.Administration]: t("Administration"),
    [EntityType.Operator]: t("Opérateur"),
    [EntityType.Producer]: t("Producteur"),
    [EntityType.Auditor]: t("Auditeur"),
    [EntityType.Trader]: t("Trader"),
    [EntityType.ExternalAdmin]: t("Administration Externe"),
  }

  const entitiesData = entities.result ?? []
  const isEmpty = entitiesData.length === 0

  return (
    <Main>
      <header>
        <h1>
          <Trans>Annuaire des sociétés enregistrées sur CarbuRe</Trans>
        </h1>
      </header>

      <section>
        <SearchInput
          clear
          debounce={250}
          label={t("Rechercher une société")}
          value={query}
          onChange={setQuery}
        />

        {isEmpty && (
          <Alert
            loading={entities.loading}
            icon={AlertCircle}
            variant="warning"
          >
            <Trans>Aucune société trouvée pour cette recherche</Trans>
          </Alert>
        )}

        {!isEmpty && (
          <Table
            loading={entities.loading}
            rows={entitiesData}
            columns={[
              {
                key: "name",
                header: t("Société"),
                cell: (e) => e.name,
                orderBy: (e) => e.name,
              },
              {
                key: "entity_type",
                header: t("Activité"),
                cell: (e) => entityTypes[e.entity_type],
                orderBy: (e) => entityTypes[e.entity_type],
              },
            ]}
          />
        )}
      </section>
    </Main>
  )
}

export default Registry
