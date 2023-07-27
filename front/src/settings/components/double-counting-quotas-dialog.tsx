import { Entity } from "carbure/types"
import Table, { Cell, Column } from "common/components/table"
import { useQuery } from "common/hooks/async"
import { formatNumber } from "common/utils/formatters"
import { DoubleCountingApplication, QuotaDetails } from "double-counting/types"
import { useTranslation } from "react-i18next"
import * as api from "../api/double-counting"

type QuotasTableProps = {
  entity: Entity
  application: DoubleCountingApplication | undefined
}

const QuotasTable = ({ entity, application: application }: QuotasTableProps) => {
  const { t } = useTranslation()

  const entityID = entity?.id ?? -1
  const dcaID = application?.id ?? -1

  const details = useQuery(api.getQuotaDetails, {
    key: "quota-details",
    params: [entityID, dcaID],
  })

  const columns: Column<QuotaDetails>[] = [
    {
      header: t("Biocarburant"),
      cell: (d) => <Cell text={d.biofuel.name} />,
    },
    {
      header: t("Matière première"),
      cell: (d) => <Cell text={d.feedstock.name} />,
    },
    { header: t("Nombre de lots"), cell: (d) => d.nb_lots },
    {
      header: t("Volume produit"),
      cell: (d) => (
        <Cell
          text={`${formatNumber(d.volume)} L`}
          sub={`${d.current_production_weight_sum_tonnes} t`}
        />
      ),
    },
    {
      header: t("Quota approuvé"),
      cell: (d) => <Cell text={formatNumber(d.approved_quota)} />,
    },
    {
      header: t("Progression des quotas"),
      cell: (d) => (
        <progress
          max={d.approved_quota}
          value={d.current_production_weight_sum_tonnes}
          title={`${d.current_production_weight_sum_tonnes} / ${d.approved_quota}`}
        />
      ),
    },
  ]

  const rows = details.result?.data.data ?? []
  return <Table loading={details.loading} columns={columns} rows={rows} />
}

export default QuotasTable
