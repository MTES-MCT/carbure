import { findEntities } from "common/api"
import { LoaderOverlay, Title } from "common/components"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { LabelInput } from "common/components/input"
import Table, { Column } from "common/components/table"
import useAPI from "common/hooks/use-api"
import { Entity } from "common/types"
import { Fragment, useEffect, useState } from "react"
import { SettingsBody, SettingsHeader } from "settings/components/common"
import { padding } from "transactions/components/list-columns"
import useSortingSelection, {
  SortingSelection,
} from "transactions/hooks/query/use-sort-by"

function sortEntities(entities: Entity[], sorter: SortingSelection) {
  const column = (sorter.column || "name") as "name" | "entity_type"

  entities.sort((a, b) => {
    const columnA = a[column].toLowerCase()
    const columnB = b[column].toLowerCase()

    if (sorter.order === "asc") {
      return columnA < columnB ? -1 : 1
    } else {
      return columnA > columnB ? -1 : 1
    }
  })
}

const COLUMNS: Column<Entity>[] = [
  padding,
  { header: "Société", sortBy: "name", render: (e) => e.name },
  { header: "Activité", sortBy: "entity_type", render: (e) => e.entity_type },
  padding,
]

const Registry = () => {
  const sorter = useSortingSelection()
  const [query, setQuery] = useState("")
  const [entities, getEntities] = useAPI(findEntities)

  useEffect(() => {
    getEntities(query)
  }, [getEntities, query])

  if (entities.data) {
    sortEntities(entities.data, sorter)
  }

  const isEmpty = !Boolean(entities.data?.length)
  const rows = (entities.data ?? []).map((e) => ({ value: e }))

  return (
    <Fragment>
      <SettingsHeader>
        <Title>Annuaire des sociétés</Title>
      </SettingsHeader>

      <SettingsBody>
        <LabelInput
          label="Rechercher une société"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />

        {isEmpty && (
          <Alert icon={AlertCircle} level="warning">
            Aucune société trouvée pour cette recherche
          </Alert>
        )}

        {!isEmpty && (
          <Table
            rows={rows}
            columns={COLUMNS}
            sortBy={sorter.column}
            order={sorter.order}
            onSort={sorter.sortBy}
          />
        )}
      </SettingsBody>

      {entities.loading && <LoaderOverlay />}
    </Fragment>
  )
}

export default Registry
