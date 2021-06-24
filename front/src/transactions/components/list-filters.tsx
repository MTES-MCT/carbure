import { useTranslation, TFunction } from "react-i18next"
import { Filters, Snapshot, TransactionQuery } from "common/types"
import { FilterSelection } from "transactions/hooks/query/use-filters"
import Select, { Option, SelectValue } from "common/components/select"

import styles from "./list-filters.module.css"
import * as api from "../api"

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
): [Filters, string, SelectValue][] {
  const filterList = filters ?? []
  
  filterList.sort(
    (a, b) =>
      FILTER_ORDER.indexOf(a as Filters) -
      FILTER_ORDER.indexOf(b as Filters)
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

  return filterList.map((field) => {
    const filter = field as Filters
    const value = selected[filter] ?? null
    return [filter, FILTER_LABELS[filter], value]
  })
}

type TransactionFiltersProps = {
  selection: FilterSelection
  filters: Snapshot["filters"] | undefined
  query: TransactionQuery
  placeholder: Filters[]
}

const TransactionFilters = ({
  selection,
  filters,
  query,
  placeholder,
}: TransactionFiltersProps) => {
  const { t } = useTranslation()

  return (
    <div className={styles.transactionFilters}>
      <div className={styles.filterGroup}>
        {mapFilters(filters, selection.selected, placeholder, t).map(
          ([filter, label, selected]) => (
            <Select 
              clear
              search
              multiple
              key={filter}
              value={selected}
              placeholder={label}
              onChange={(value) => selection.select(filter, value)}
              getOptions={api.getFilters}
              getArgs={[filter, query, t]}
            />
          )
        )}
      </div>
    </div>
  )
}

export default TransactionFilters
