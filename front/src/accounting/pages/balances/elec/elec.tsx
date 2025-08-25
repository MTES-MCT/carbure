import { useQuery } from "common/hooks/async"
import { useBalancesElecColumns } from "./elec.hooks"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import { Pagination } from "common/components/pagination2/pagination"
import { ElecOperationsQueryBuilder } from "accounting/types"
import { NoResult } from "common/components/no-result2"
import { getElecBalances } from "accounting/api/elec-balances"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { useUnit } from "common/hooks/unit"
import { Unit } from "common/types"
import { useQueryBuilder } from "common/hooks/query-builder-2"

const BalancesElec = () => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
  const columns = useBalancesElecColumns()

  const { state, actions, query } =
    useQueryBuilder<ElecOperationsQueryBuilder["config"]>()

  const { result, loading } = useQuery(getElecBalances, {
    key: "elec-balances",
    params: [query],
  })

  return (
    <>
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
                unit: Unit.MJ,
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

export default BalancesElec
