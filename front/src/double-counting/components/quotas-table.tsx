import { Cell, Column } from "common/components/table2"
import { formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { DoubleCountingQuota } from "../types"
import YearTable from "./year-table"
import { useRoutes } from "common/hooks/routes"
import useEntity from "common/hooks/entity"
import { toSearchParams } from "common/services/api-fetch"
import { Button } from "common/components/button2"

type QuotasTableProps = {
  quotas: DoubleCountingQuota[]
  dc_agreement_id: string
}

export const QuotasTable = ({ quotas, dc_agreement_id }: QuotasTableProps) => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const entity = useEntity()

  function getPreviewURL(quota: DoubleCountingQuota) {
    const url = entity.isProducer
      ? routes.BIOFUELS(quota.year).SENT + "/history"
      : routes.BIOFUELS_CONTROLS(quota.year).LOTS

    const query = {
      biofuels: quota.biofuel.code,
      feedstocks: quota.feedstock.code,
      certificate_id: dc_agreement_id,
    }

    console.log(`${url}?${toSearchParams(query)}`)
    return `${url}?${toSearchParams(query)}`
  }

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
      header: t("Lots concernés"),
      cell: (p) =>
        !p.lot_count ? (
          t("-")
        ) : (
          <Button customPriority="link" linkProps={{ to: getPreviewURL(p) }}>
            {t("Voir les lots")} ({formatNumber(p.lot_count ?? 0)})
          </Button>
        ),
    },
    {
      header: t("Quantité incorporée"),
      cell: (p) => <Cell text={formatNumber(p.production_tonnes) + "t"} />,
    },
    {
      header: t("Progression"),
      cell: (p) => <Cell text={Math.round(p.quotas_progression * 100) + "%"} />,
    },
  ]

  return <YearTable columns={quotasColumns} rows={quotas} />
}
