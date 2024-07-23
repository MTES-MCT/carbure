import { Cell, Column } from "common/components/table"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { DoubleCountingQuota } from "../types"
import YearTable from "./year-table"

type QuotasTableProps = {
  quotas: DoubleCountingQuota[]
}

export const QuotasTable = ({ quotas }: QuotasTableProps) => {
  const { t } = useTranslation()

  const quotasColumns: Column<DoubleCountingQuota>[] = [
    {
      header: t("Matière première"),
      cell: (p) => <Cell text={t(p.feedstock.code, { ns: "feedstocks" })} />,
    },
    {
      header: t("Biocarburant"),
      cell: (p) => <Cell text={t(p.biofuel.code, { ns: "biofuels" })} />,
    },
    {
      header: t("Quota approuvé"),
      cell: (p) => <Cell text={formatNumber(p.approved_quota ?? 0) + "t"} />,
    },
    {
      header: t("Nombre de lots"),
      cell: (p) => <Cell text={formatNumber(p.lot_count ?? 0)} />,
    },
    {
      header: t("Volume produit"),
      cell: (p) => <Cell text={formatNumber(p.production_tonnes) + "t"} />,
    },
    {
      header: t("Progression"),
      cell: (p) => <Cell text={Math.round(p.quotas_progression * 100) + "%"} />,
    },
  ]

  return <YearTable columns={quotasColumns} rows={quotas} />
}
