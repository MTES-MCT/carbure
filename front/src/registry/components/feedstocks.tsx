import { findFeedstocks } from "carbure/api"
import Table from "common/components/table"
import { useQuery } from "common/hooks/async"
import { Fragment } from "react"
import { useTranslation } from "react-i18next"

const Feedstocks = () => {
  const { t } = useTranslation()

  const feedstocks = useQuery(findFeedstocks, {
    key: "feedstocks",
    params: [""],
  })

  const feedstocksData = feedstocks.result ?? []

  return (
    <Fragment>
      <Table
        loading={feedstocks.loading}
        rows={feedstocksData}
        columns={[
          {
            key: "name",
            header: t("Matière première"),
            cell: (e) => e.name,
            orderBy: (e) => e.name,
          },
          {
            key: "category",
            header: t("Catégorie"),
            cell: (e) => e.category,
            orderBy: (e) => e.category,
          },
        ]}
      />
    </Fragment>
  )
}

export default Feedstocks
