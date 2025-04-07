import { useQuery } from "common/hooks/async"

import useEntity from "common/hooks/entity"
import { useBalancesColumns, useGetFilterOptions } from "./balances.hooks"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { Pagination } from "common/components/pagination2/pagination"
import { OperationsStatus, BalancesFilter } from "accounting/types"
import { NoResult } from "common/components/no-result2"
import { getBalances } from "accounting/api/balances"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { useUnit } from "common/hooks/unit"

const Balances = () => {
  const entity = useEntity()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
  const columns = useBalancesColumns()

  const filterLabels = {
    [BalancesFilter.sector]: t("Filière"),
    [BalancesFilter.customs_category]: t("Catégorie"),
    [BalancesFilter.biofuel]: t("Biocarburants"),
  }

  const [state, actions] = useCBQueryParamsStore<OperationsStatus[], undefined>(
    entity
  )

  const query = useCBQueryBuilder<[], OperationsStatus[], undefined>(state)

  const { result, loading } = useQuery(getBalances, {
    key: "balances",
    params: [query],
  })

  const getFilterOptions = useGetFilterOptions(query)

  return (
    <>
      <FilterMultiSelect2
        filterLabels={filterLabels}
        selected={state.filters}
        onSelect={actions.setFilters}
        getFilterOptions={getFilterOptions}
      />
      {!loading &&
      result?.data?.results &&
      result?.data?.results?.length === 0 ? (
        <NoResult />
      ) : (
        <>
          <RecapQuantity
            text={t("Le solde affiché représente {{total}}", {
              total: formatUnit(result?.data?.total_quantity ?? 0, {
                fractionDigits: 0,
              }),
            })}
          />
          <Table
            columns={columns}
            rows={result?.data?.results ?? []}
            loading={loading}
          />
          <Pagination
            defaultPage={query.page}
            total={result?.data?.count ?? 0}
            limit={state.limit}
            onLimit={actions.setLimit}
            disabled={loading}
          />
        </>
      )}
    </>
  )
}

export default Balances
