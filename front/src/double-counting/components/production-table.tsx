import Button from "common/components/button"
import { NumberInput } from "common/components/input"
import { Cell, Column } from "common/components/table"
import { formatNumber, formatPercentage } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { DoubleCountingProduction, DoubleCountingSourcing } from "../types"
import YearTable from "./year-table"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"

type ProductionTableProps = {
  hasAgreement?: boolean

  quotas?: Record<string, number>
  production: DoubleCountingProduction[]
  sourcing: DoubleCountingSourcing[]
  setQuotas?: (quotas: Record<string, number>) => void
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
      header: t("Prod. estimée"),
      cell: (p) => <Cell text={formatNumber(p.estimated_production ?? 0)} />,
    },
    entity.isAdmin && {
      header: t("Rendement estimé"),
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

  if (hasAgreement) {
    productionColumns?.push({
      header: t("Quota approuvé"),
      cell: (p) => <Cell text={formatNumber(p.approved_quota)} />,
    })
  }

  if (quotas && setQuotas) {
    productionColumns?.push({
      header: t("Quota approuvé"),
      cell: (p) => (
        <ApprovedQuotasCell
          production={p}
          quotas={quotas}
          setQuotas={setQuotas}
        />
      ),
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
  // const [approvedQuota, setApprovedQuota] = useState(production.approved_quota)

  const onSetMaximumVolume = () => {
    // setApprovedQuota(production.requested_quota)
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
        // setApprovedQuota(value)
        setQuotas({
          ...quotas,
          [production.id]: value,
        })
      }}
      rightContent={
        <Button
          label={t("Max")}
          action={onSetMaximumVolume}
          variant="primary"
        />
      }
    />
  )
}
