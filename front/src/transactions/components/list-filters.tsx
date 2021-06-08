import { Filters, Snapshot } from "common/types"
import { FilterSelection } from "transactions/hooks/query/use-filters"

import Select, { Option, SelectValue } from "common/components/select"

import styles from "./list-filters.module.css"

const FILTER_ORDER = [
  Filters.DeliveryStatus,
  Filters.Periods,
  Filters.Biocarburants,
  Filters.MatieresPremieres,
  Filters.CountriesOfOrigin,
  Filters.Vendors,
  Filters.Clients,
  Filters.ProductionSites,
  Filters.DeliverySites,
  Filters.AddedBy,
  Filters.Errors,
  Filters.Forwarded,
  Filters.Mac,
  Filters.AckedByAdmin,
  Filters.HighlightedByAdmin,
]

const FILTER_LABELS = {
  [Filters.DeliveryStatus]: "Livraison",
  [Filters.Periods]: "Périodes",
  [Filters.ProductionSites]: "Sites de production",
  [Filters.MatieresPremieres]: "Matières Premières",
  [Filters.Biocarburants]: "Biocarburants",
  [Filters.CountriesOfOrigin]: "Pays d'origine",
  [Filters.DeliverySites]: "Sites de livraison",
  [Filters.Clients]: "Clients",
  [Filters.Vendors]: "Fournisseurs",
  [Filters.AddedBy]: "Ajouté par",
  [Filters.Errors]: "Incohérences",
  [Filters.Forwarded]: "Lots Transférés",
  [Filters.Mac]: "Mises à consommation",
  [Filters.AckedByAdmin]: "Marqués comme vus",
  [Filters.HighlightedByAdmin]: "Mis de côté",
}

export function mapFilters(
  filters: Snapshot["filters"] | undefined,
  selected: FilterSelection["selected"],
  placeholder: Filters[]
): [Filters, string, SelectValue, Option[]][] {
  const filterList: [string, Option[]?][] =
    typeof filters === "undefined"
      ? placeholder.map((f) => [f, []])
      : Object.entries(filters)

  filterList.sort(
    (a, b) =>
      FILTER_ORDER.indexOf(a[0] as Filters) -
      FILTER_ORDER.indexOf(b[0] as Filters)
  )

  return filterList.map(([key, options]) => {
    const filter = key as Filters
    const value = selected[filter] ?? null
    return [filter, FILTER_LABELS[filter], value, options ?? []]
  })
}

type TransactionFiltersProps = {
  selection: FilterSelection
  filters: Snapshot["filters"] | undefined
  placeholder: Filters[]
}

const TransactionFilters = ({
  selection,
  filters,
  placeholder,
}: TransactionFiltersProps) => (
  <div className={styles.transactionFilters}>
    <div className={styles.filterGroup}>
      {mapFilters(filters, selection.selected, placeholder).map(
        ([filter, label, selected, options]) => (
          <Select
            clear
            search
            multiple
            key={filter}
            value={selected}
            placeholder={label}
            options={options}
            onChange={(value) => selection.select(filter, value)}
          />
        )
      )}
    </div>
  </div>
)

export default TransactionFilters
