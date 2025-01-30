import { useQuery } from "common/hooks/async"
import * as api from "./api"
import useEntity from "carbure/hooks/entity"
import { useBalancesColumns } from "./balances.hooks"
import { Table } from "common/components/table2"

export const Balances = () => {
  const entity = useEntity()

  const { result } = useQuery(api.getBalances, {
    key: "balances",
    params: [entity.id],
  })

  const columns = useBalancesColumns()

  return (
    <>
      <Table columns={columns} rows={result?.data?.results ?? []} />
    </>
  )
}
