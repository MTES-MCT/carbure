import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import { findEntities } from "carbure/api"
import { Main } from "common/components/scaffold"
import { SearchInput } from "common/components/input"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import Table from "common/components/table"
import useTitle from "common/hooks/title"
import { getEntityTypeLabel } from "carbure/utils/normalizers"

const Registry = () => {
  const { t } = useTranslation()
  useTitle(t("Annuaire"))

  const [query, setQuery] = useState<string | undefined>("")

  const entities = useQuery(findEntities, {
    key: "entities",
    params: [query],
  })

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
                cell: (e) => getEntityTypeLabel(e.entity_type),
                orderBy: (e) => getEntityTypeLabel(e.entity_type),
              },
            ]}
          />
        )}
      </section>
    </Main>
  )
}

export default Registry
