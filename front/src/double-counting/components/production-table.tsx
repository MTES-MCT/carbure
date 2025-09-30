import { Button } from "common/components/button2"
import { NumberInput } from "common/components/inputs2"
import { Cell, Column } from "common/components/table2"
import { formatNumber, formatPercentage } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { DoubleCountingProduction, DoubleCountingSourcing } from "../types"
import YearTable from "./year-table"
import useEntity from "common/hooks/entity"
import { compact } from "common/utils/collection"

type ProductionTableProps = {
  quotas?: Record<string, number>
  production: DoubleCountingProduction[]
  sourcing: DoubleCountingSourcing[]
  setQuotas?: (quotas: Record<string, number>) => void
  hasAgreement?: boolean
}

export const ProductionTable = ({
  hasAgreement,
  sourcing,
  quotas,
  production,
  setQuotas,
}: ProductionTableProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const canWrite = entity.canWrite()

  const productionColumns: Column<DoubleCountingProduction>[] = compact([
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
      cell: (p) => <Cell text={formatNumber(p.estimated_production ?? 0)} />,
    },
    (entity.isAdmin || entity.isExternal) && {
      header: t("Ratio prod."),
      cell: (p) => {
        // Find sources related to the production
        const sources = sourcing.filter(
          (source) =>
            source.feedstock.code === p.feedstock.code && p.year === source.year
        )

        // Calculate sum weight
        const metricTonnes = sources.reduce(
          (sum, source) => source.metric_tonnes + sum,
          0
        )

        const estimatedEfficiency = sources.length
          ? (p.estimated_production / metricTonnes) * 100
          : null

        return (
          <Cell
            text={
              estimatedEfficiency ? formatPercentage(estimatedEfficiency) : ""
            }
          />
        )
      },
    },
    {
      header: t("Quota demandé"),
      cell: (p) => <Cell text={formatNumber(p.requested_quota)} />,
    },
  ])

  if (!canWrite || hasAgreement) {
    productionColumns?.push({
      header: t("Quota approuvé"),
      cell: (p) => <Cell text={formatNumber(p.approved_quota)} />,
    })
  }

  if (canWrite && quotas && setQuotas) {
    productionColumns?.push({
      header: t("Quota approuvé"),
      cell: (p) => (
        <ApprovedQuotasCell
          production={p}
          quotas={quotas}
          setQuotas={setQuotas}
        />
      ),
      style: { minWidth: "200px" },
    })
  }

  return <YearTable columns={productionColumns} rows={production} />
}

interface ApprovedQuotasCellProps {
  production: DoubleCountingProduction
  quotas: Record<string, number>
  setQuotas: (quotas: Record<string, number>) => void
}
const ApprovedQuotasCell = ({
  production,
  quotas,
  setQuotas,
}: ApprovedQuotasCellProps) => {
  const { t } = useTranslation()

  const onSetMaximumVolume = () => {
    setQuotas({
      ...quotas,
      [production.id]: production.requested_quota,
    })
  }

  return (
    <NumberInput
      value={quotas[production.id]}
      max={production.requested_quota}
      onChange={(value) => {
        setQuotas({
          ...quotas,
          [production.id]: value,
        })
      }}
      addon={<Button onClick={onSetMaximumVolume}>{t("Max")}</Button>}
    />
  )
}
