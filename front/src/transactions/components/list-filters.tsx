import { useTranslation, TFunction } from "react-i18next"
import { Filters, Snapshot } from "common/types"
import { FilterSelection } from "transactions/hooks/query/use-filters"
import Select, {
  MultipleSelect,
  Option,
  SelectValue,
} from "common/components/select"

import styles from "./list-filters.module.css"

import { findBiocarburants } from "common/api"

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
  Filters.HiddenByAdmin,
  Filters.HiddenByAuditor,
]

export function mapFilters(
  filters: Snapshot["filters"] | undefined,
  selected: FilterSelection["selected"],
  placeholder: Filters[],
  t: TFunction<"translation">
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

  const FILTER_LABELS = {
    [Filters.DeliveryStatus]: t("Livraison"),
    [Filters.Periods]: t("Périodes"),
    [Filters.ProductionSites]: t("Sites de production"),
    [Filters.MatieresPremieres]: t("Matières Premières"),
    [Filters.Biocarburants]: t("Biocarburants"),
    [Filters.CountriesOfOrigin]: t("Pays d'origine"),
    [Filters.DeliverySites]: t("Sites de livraison"),
    [Filters.Clients]: t("Clients"),
    [Filters.Vendors]: t("Fournisseurs"),
    [Filters.AddedBy]: t("Ajouté par"),
    [Filters.Errors]: t("Incohérences"),
    [Filters.Forwarded]: t("Lots Transférés"),
    [Filters.Mac]: t("Mises à consommation"),
    [Filters.HiddenByAdmin]: t("Lots ignorés"),
    [Filters.HiddenByAuditor]: t("Lots ignorés"),
  }

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

function findBC(query: string): Promise<Option[]> {
  return findBiocarburants(query).then((bcs) =>
    bcs.map((bc) => ({
      value: bc.code,
      label: bc.name,
    }))
  )
}

const TransactionFilters = ({
  selection,
  filters,
  placeholder,
}: TransactionFiltersProps) => {
  const { t } = useTranslation()

  const filter = filters?.[Filters.Biocarburants]

  return (
    <div className={styles.transactionFilters}>
      <div className={styles.filterGroup}>
        <MultipleSelect value={filter} getOptions={findBC} />

        {mapFilters(filters, selection.selected, placeholder, t).map(
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
}

export default TransactionFilters
