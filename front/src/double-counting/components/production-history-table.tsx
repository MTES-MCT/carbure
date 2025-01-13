import { Cell, Column } from "common/components/table"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { DoubleCountingProductionHistory } from "../types"
import YearTable from "./year-table"
import { compact } from "common/utils/collection"

type ProductionHistoryTableProps = {
  production: DoubleCountingProductionHistory[]
}

export const ProductionHistoryTable = ({
  production,
}: ProductionHistoryTableProps) => {
  const { t } = useTranslation()

  const productionColumns: Column<DoubleCountingProductionHistory>[] = compact([
    {
      header: t("Matière première"),
      cell: (p) => <Cell text={t(p.feedstock.code, { ns: "feedstocks" })} />,
    },
    {
      header: t("Biocarburant"),
      cell: (p) => <Cell text={t(p.biofuel.code, { ns: "biofuels" })} />,
    },
    {
      header: t("Prod. max"),
      cell: (p) => <Cell text={formatNumber(p.max_production_capacity ?? 0)} />,
    },
    {
      header: t("Prod. effective"),
      cell: (p) => <Cell text={formatNumber(p.effective_production ?? 0)} />,
    },
  ])

  return <YearTable columns={productionColumns} rows={production} />
}
