import { Column, Table } from "common/components/table2"
import {
  BiomethaneSupplyInput,
  BiomethaneSupplyInputQueryBuilder,
  BiomethaneSupplyInputResponse,
} from "../../types"
import { NoResult } from "common/components/no-result2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { useTranslation } from "react-i18next"
import { useSupplyPlanColumns } from "./supply-plan-table.hooks"
import { useLocation } from "react-router-dom"
import { Pagination } from "common/components/pagination2"

type SupplyPlanTableProps = {
  supplyPlan: {
    supplyInputs?: BiomethaneSupplyInputResponse
    loading: boolean
  }
  queryBuilder: Omit<BiomethaneSupplyInputQueryBuilder, "config">
  columns?: Column<BiomethaneSupplyInput>[]
}
export const SupplyPlanTable = ({
  supplyPlan,
  queryBuilder,
  columns: overiddenColumns = [],
}: SupplyPlanTableProps) => {
  const { t } = useTranslation()
  const _columns = useSupplyPlanColumns()
  const location = useLocation()

  const columns = overiddenColumns.length > 0 ? overiddenColumns : _columns

  if (
    !supplyPlan.loading &&
    (!supplyPlan.supplyInputs || supplyPlan.supplyInputs?.count === 0)
  ) {
    return <NoResult />
  }

  return (
    <>
      <RecapQuantity
        text={t("{{total}} tonnes annuelles", {
          total: supplyPlan.supplyInputs?.annual_volumes_in_t ?? 0,
        })}
      />
      <Table
        rows={supplyPlan.supplyInputs?.results ?? []}
        columns={columns}
        loading={supplyPlan.loading}
        rowLink={(row) => ({
          pathname: location.pathname,
          search: location.search,
          hash: `supply-input/${row.id}`,
        })}
      />
      <Pagination
        defaultPage={queryBuilder.query.page}
        total={supplyPlan.supplyInputs?.count ?? 0}
        limit={queryBuilder.state.limit}
        onLimit={queryBuilder.actions.setLimit}
        disabled={supplyPlan.loading}
      />
    </>
  )
}
