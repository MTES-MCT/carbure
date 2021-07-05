import { useTranslation, TFunction } from "react-i18next"
import { EntityType, Filters, Snapshot, TransactionQuery } from "common/types"
import { FilterSelection } from "transactions/hooks/query/use-filters"
import Select, { SelectValue } from "common/components/select"

import styles from "./list-filters.module.css"
import { getFilters, getAdminFilters, getAuditorFilters } from "../api"
import { getStockFilters } from "stocks/api"
import { EntitySelection } from "carbure/hooks/use-entity"

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
  const filterList = filters ?? placeholder

  filterList.sort(
    (a, b) =>
      FILTER_ORDER.indexOf(a as Filters) - FILTER_ORDER.indexOf(b as Filters)
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

function filterGetter(entity?: EntitySelection, stock?: boolean) {
  if (stock) return getStockFilters

  switch (entity?.entity_type) {
    case EntityType.Administration:
      return getAdminFilters
    case EntityType.Auditor:
      return getAuditorFilters
    default:
      return getFilters
  }
}

type TransactionFiltersProps = {
  selection: FilterSelection
  filters: Snapshot["filters"] | undefined
  query: TransactionQuery
  placeholder: Filters[]
  entity: EntitySelection
  stock?: boolean
}

const TransactionFilters = ({
  selection,
  filters,
  query,
  placeholder,
  entity,
  stock,
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
              getOptions={filterGetter(entity, stock)}
              getArgs={[filter, query, t]}
            />
          )
        )}
      </div>
    </div>
  )
}

export default TransactionFilters
