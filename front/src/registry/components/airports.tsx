import { findAirports } from "carbure/api"
import Alert from "common/components/alert"
import { AlertCircle } from "common/components/icons"
import { SearchInput } from "common/components/input"
import Table from "common/components/table"
import { useQuery } from "common/hooks/async"
import { Fragment, useState } from "react"
import { useTranslation } from "react-i18next"

export const Airports = () => {
  const { t } = useTranslation()
  const [query, setQuery] = useState<string | undefined>("")
  const airports = useQuery(findAirports, {
    key: "airports",
    params: [query, true],
  })

  const airportsData = airports.result ?? []
  const isEmpty = airportsData.length === 0

  return (
    <Fragment>
      <SearchInput
        clear
        debounce={250}
        label={t("Rechercher un aéroport")}
        value={query}
        onChange={setQuery}
      />

      {isEmpty && (
        <Alert loading={airports.loading} icon={AlertCircle} variant="warning">
          {t("Aucun aéroport trouvé pour cette recherche")}
        </Alert>
      )}

      {!isEmpty && (
        <Table
          loading={airports.loading}
          rows={airportsData}
          columns={[
            {
              key: "name",
              header: t("Aéroport"),
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
              key: "icao_code",
              header: t("Code ICAO"),
              cell: (e) => e.icao_code,
              orderBy: (e) => e.icao_code ?? "",
            },
          ]}
        />
      )}
    </Fragment>
  )
}
