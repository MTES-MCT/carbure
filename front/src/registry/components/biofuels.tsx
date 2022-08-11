import { findBiofuels } from "carbure/api"
import Table from "common/components/table"
import { useQuery } from "common/hooks/async"
import { Fragment } from "react"
import { useTranslation } from "react-i18next"

const Biofuels = () => {
  const { t } = useTranslation()

  const biofuels = useQuery(findBiofuels, {
    key: "biofuels",
    params: [""],
  })

  const biofuelsData = biofuels.result ?? []

  return (
    <Fragment>
      <Table
        loading={biofuels.loading}
        rows={biofuelsData}
        columns={[
          {
            key: "name",
            header: t("Biocarburant"),
            cell: (e) => e.name,
            orderBy: (e) => e.name,
          },
        ]}
      />
    </Fragment>
  )
}

export default Biofuels
