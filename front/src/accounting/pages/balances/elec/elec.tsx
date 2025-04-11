import { useQuery } from "common/hooks/async"

import useEntity from "common/hooks/entity"
import { useBalancesElecColumns } from "./elec.hooks"
import { Table } from "common/components/table2"
import { useTranslation } from "react-i18next"
import {
  useCBQueryBuilder,
  useCBQueryParamsStore,
} from "common/hooks/query-builder-2"
import { Pagination } from "common/components/pagination2/pagination"
import { ElecOperationsStatus } from "accounting/types"
import { NoResult } from "common/components/no-result2"
import { getBalances } from "accounting/api/elec-balances"
import { RecapQuantity } from "common/molecules/recap-quantity"
import { useUnit } from "common/hooks/unit"
import { Unit } from "common/types"

const BalancesElec = () => {
  const entity = useEntity()
  const { t } = useTranslation()
  const { formatUnit } = useUnit()
  const columns = useBalancesElecColumns()

  const [state, actions] = useCBQueryParamsStore<
    ElecOperationsStatus[],
    undefined
  >(entity)

  const query = useCBQueryBuilder<[], ElecOperationsStatus[], undefined>(state)

  const { result, loading } = useQuery(getBalances, {
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
