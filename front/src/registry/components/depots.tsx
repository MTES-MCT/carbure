import { findDepots } from "carbure/api"
import { Alert } from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { SearchInput } from "common/components/input"
import Table from "common/components/table"
import { useQuery } from "common/hooks/async"
import { Fragment, useState } from "react"
import { Trans, useTranslation } from "react-i18next"

const Depots = () => {
  const { t } = useTranslation()
  const [query, setQuery] = useState<string | undefined>("")
  const depots = useQuery(findDepots, {
    key: "depots",
    params: [query, true],
  })

  const depotsData = depots.result ?? []
  const isEmpty = depotsData.length === 0

  return (
    <Fragment>
      <SearchInput
        clear
        debounce={250}
        label={t("Rechercher un dépôt")}
        value={query}
        onChange={setQuery}
      />

      {isEmpty && (
        <Alert loading={depots.loading} icon={AlertCircle} variant="warning">
          <Trans>Aucun dépôt trouvé pour cette recherche</Trans>
        </Alert>
      )}

      {!isEmpty && (
        <Table
          loading={depots.loading}
          rows={depotsData}
          columns={[
            {
              key: "name",
              header: t("Dépôt"),
              cell: (e) => e.name,
              orderBy: (e) => e.name,
            },
            {
              key: "city",
              header: t("Ville"),
              cell: (e) => e.city,
              orderBy: (e) => e.city ?? "",
            },
            {
              key: "depot_id",
              header: t("ID"),
              cell: (e) => e.depot_id,
              orderBy: (e) => e.depot_id,
            },
          ]}
        />
      )}
    </Fragment>
  )
}

export default Depots
