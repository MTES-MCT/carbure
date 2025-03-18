import { FilterMultiSelect2 } from "common/molecules/filter-multiselect2"
import { OperationsFilter, OperationsStatus } from "./types"
import { useTranslation } from "react-i18next"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import useEntity from "common/hooks/entity"
import * as api from "./api"
import { Table } from "common/components/table2"
import { useQuery } from "common/hooks/async"
import { useGetFilterOptions, useOperationsColumns } from "./operations.hooks"
import { Pagination } from "common/components/pagination2/pagination"
import HashRoute from "common/components/hash-route"
import { OperationDetail } from "./pages/operation-detail"
import { usePrivateNavigation } from "common/layouts/navigation"
const currentYear = new Date().getFullYear()

export const Operations = ({
  setOperationCount,
}: {
  setOperationCount: (count: number) => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  usePrivateNavigation(t("Comptabilité"))
  const filterLabels = {
    [OperationsFilter.depot]: t("Dépôts"),
    [OperationsFilter.status]: t("Statut"),
    [OperationsFilter.sector]: t("Filière"),
    [OperationsFilter.customs_category]: t("Catégorie"),
    [OperationsFilter.biofuel]: t("Biocarburants"),
    [OperationsFilter.period]: t("Date"),
    [OperationsFilter.type]: t("Débit / Crédit"),
    [OperationsFilter.operation]: t("Opération"),
    [OperationsFilter.from_to]: t("Redevable"),
  }

  const [state, actions] = useCBQueryParamsStore<OperationsStatus[], undefined>(
    entity,
    currentYear
  )

  const query = useCBQueryBuilder<[], OperationsStatus[], undefined>(state)

  const { result, loading } = useQuery(api.getOperations, {
    key: "operations",
    params: [query],
    onSuccess: (data) => {
      setOperationCount(data?.data?.count ?? 0)
    },
  })

  const columns = useOperationsColumns({
    onClickSector: (sector) => {
      actions.setFilters({
        ...state.filters,
        sector: [sector],
      })
    },
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
      <Table
        columns={columns}
        rows={result?.data?.results ?? []}
        rowLink={(row) => ({
          pathname: location.pathname,
          search: location.search,
          hash: `operation/${row.id}`,
        })}
        loading={loading}
      />
      <Pagination
        defaultPage={query.page}
        total={result?.data?.count ?? 0}
        limit={query.limit}
      />
      <HashRoute path="operation/:id" element={<OperationDetail />} />
    </>
  )
}
