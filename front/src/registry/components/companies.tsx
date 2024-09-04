import { findEntities } from "carbure/api"
import { getEntityTypeLabel } from "carbure/utils/normalizers"
import { SearchInput } from "common/components/input"
import NoResult from "common/components/no-result"
import Table from "common/components/table"
import { useQuery } from "common/hooks/async"
import { Fragment, useState } from "react"
import { useTranslation } from "react-i18next"

const Companies = () => {
  const { t } = useTranslation()
  const [query, setQuery] = useState<string | undefined>("")
  const entities = useQuery(findEntities, {
    key: "entities",
    params: [query],
  })

  const entitiesData = entities.result ?? []
  const isEmpty = entitiesData.length === 0

  return (
    <Fragment>
      <SearchInput
        clear
        debounce={250}
        label={t("Rechercher une société")}
        value={query}
        onChange={setQuery}
      />

      {isEmpty && (
        <NoResult
          label={t("Aucune société trouvée pour cette recherche")}
          loading={entities.loading}
        />
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
    </Fragment>
  )
}

export default Companies
