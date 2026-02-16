import { Table } from "common/components/table2"
import {
  BiomethaneSupplyInputQueryBuilder,
  BiomethaneSupplyInputResponse,
} from "../../types"
import { NoResult } from "common/components/no-result2"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { useTranslation } from "react-i18next"
import { useSupplyPlanColumns } from "./supply-plan-table.hooks"
import { useLocation } from "react-router-dom"
import { Pagination } from "common/components/pagination2"
import HashRoute from "common/components/hash-route"
import { SupplyInputDialog } from "../../supply-input-dialog"

type SupplyPlanTableProps = {
  supplyPlan: {
    supplyInputs?: BiomethaneSupplyInputResponse
    loading: boolean
  }
  queryBuilder: Omit<BiomethaneSupplyInputQueryBuilder, "config">
}
export const SupplyPlanTable = ({
  supplyPlan,
  queryBuilder,
}: SupplyPlanTableProps) => {
  const { t } = useTranslation()
  const columns = useSupplyPlanColumns()
  const location = useLocation()

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
      <HashRoute path="/supply-input/:id" element={<SupplyInputDialog />} />
    </>
  )
}
