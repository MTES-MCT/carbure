import { useQuery } from "common/hooks/async"
import * as api from "./api"
import useEntity from "carbure/hooks/entity"
import { useBalancesColumns } from "./balances.hooks"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { OperationsStatus } from "material-accounting/operations/types"
import { Pagination } from "common/components/pagination2/pagination"

export const Balances = () => {
  const entity = useEntity()
  const { t } = useTranslation()

  const columns = useBalancesColumns()

  const filterLabels = {
    sector: t("Filière"),
    category: t("Catégorie"),
    biofuel: t("Biocarburants"),
  }

  const [state, actions] = useCBQueryParamsStore<OperationsStatus[], undefined>(
    entity
  )

  const query = useCBQueryBuilder<[], OperationsStatus[], undefined>(state)

  const { result } = useQuery(api.getBalances, {
    key: "balances",
    params: [query],
  })

  return (
    <>
      <FilterMultiSelect2
        filterLabels={filterLabels}
        selected={state.filters}
        onSelect={actions.setFilters}
        getFilterOptions={() => []}
      />
      <Table columns={columns} rows={result?.data?.results ?? []} />
      <Pagination
        defaultPage={query.page}
        total={result?.data?.count ?? 0}
        limit={query.limit}
      />
    </>
  )
}
