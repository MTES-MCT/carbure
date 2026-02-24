import Table from "common/components/table"
import { useFeedstocksByEntity } from "common/hooks/api/use-feedstocks"
import { Fragment } from "react"
import { useFeedstocksColumns } from "./feedstocks.hooks"

const Feedstocks = () => {
  const columns = useFeedstocksColumns()
  const feedstocks = useFeedstocksByEntity()

  const feedstocksData = feedstocks.result ?? []

  return (
    <Fragment>
      <Table
        loading={feedstocks.loading}
        rows={feedstocksData}
        columns={columns}
      />
    </Fragment>
  )
}

export default Feedstocks
