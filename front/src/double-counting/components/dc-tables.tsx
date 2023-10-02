import { useTranslation } from "react-i18next"
import { Entity, EntityType } from "carbure/types"
import {
  Admin,
  DoubleCountingSourcing,
  DoubleCountingProduction,
  DoubleCountingApplicationDetails,
  DoubleCountingSourcingAggregation,
} from "../types"
import Table, { Column, Cell } from "common/components/table"
import { NumberInput } from "common/components/input"
import YearTable from "./year-table"
import { formatDate, formatNumber } from "common/utils/formatters"
import Checkbox from "common/components/checkbox"
import { useState } from "react"
import Button from "common/components/button"

type ValidationStatus = {
  approved: boolean
  date: string
  user: string
  entity: string
}

type SourcingTableProps = {
  sourcing: DoubleCountingSourcing[]
  actions?: Column<DoubleCountingSourcing>
}

export const SourcingTable = ({ sourcing }: SourcingTableProps) => {
  const { t } = useTranslation()

  const columns: Column<DoubleCountingSourcing>[] = [
    {
      header: t("Matière première"),
      cell: (s) => <Cell text={t(s.feedstock.code, { ns: "feedstocks" })} />,
    },
    {
      header: t("Poids en tonnes"),
      cell: (s) => <Cell text={formatNumber(s.metric_tonnes)} />,
    },
    {
      header: t("Origine"),
      cell: (s) => (
        s.origin_country?.code_pays ? (
          <Cell text={t(s.origin_country.code_pays, { ns: "countries" })} />
        )
          : null
      ),
    },
    {
      header: t("Approvisionnement"),
      cell: (s) =>
        s.supply_country && (
          <Cell text={t(s.supply_country.code_pays, { ns: "countries" })} />
        ),
    },
    {
      header: t("Transit"),
      cell: (s) =>
        s.transit_country ? (
          <Cell text={t(s.transit_country.code_pays, { ns: "countries" })} />
        ) : "-",
    },
  ]

  return <YearTable columns={columns} rows={sourcing} />
}

type SourcingAggregationTableProps = {
  sourcing: DoubleCountingSourcingAggregation[]
}

export const SourcingAggregationTable = ({
  sourcing,
}: SourcingAggregationTableProps) => {
  const { t } = useTranslation()

  const columns: Column<DoubleCountingSourcingAggregation>[] = [
    {
      header: t("Matière première"),
      cell: (s) => <Cell text={t(s.feedstock.code, { ns: "feedstocks" })} />,
    },
    {
      header: t("Poids total en tonnes"),
      cell: (s) => <Cell text={formatNumber(s.sum)} />,
    }
  ]

  return <YearTable columns={columns} rows={sourcing} />
}


export const SourcingFullTable = ({ sourcing }: { sourcing: DoubleCountingSourcing[] }) => {

  const [aggregateSourcing, setAggregateSourcing] = useState(true);
  const { t } = useTranslation()

  const aggregateDoubleCountingSourcing = (data: DoubleCountingSourcing[]): DoubleCountingSourcingAggregation[] => {
    const aggregationMap = new Map<string, DoubleCountingSourcingAggregation>();
    for (const item of data) {
      const key = `${item.feedstock.code}_${item.year}`;
      const aggregation = aggregationMap.get(key);

      if (aggregation) {
        aggregation.sum += item.metric_tonnes;
        aggregation.count += 1;
      } else {
        aggregationMap.set(key, {
          year: item.year,
          sum: item.metric_tonnes,
          count: 1,
          feedstock: item.feedstock
        });
      }
    }

    return Array.from(aggregationMap.values());
  }

  const aggregated_sourcing: DoubleCountingSourcingAggregation[] = aggregateDoubleCountingSourcing(sourcing);

  return <>

    {sourcing?.length > 0 &&
      <Checkbox readOnly value={aggregateSourcing} onChange={() => setAggregateSourcing(!aggregateSourcing)}>
        {t("Agréger les données d'approvisionnement par matière première")}
      </Checkbox>
    }
    {!aggregateSourcing &&
      <SourcingTable
        sourcing={sourcing ?? []}
      />
    }
    {aggregateSourcing &&
      <SourcingAggregationTable
        sourcing={aggregated_sourcing ?? []}
      />
    }
  </>
}

type ProductionTableProps = {
  hasAgreement?: boolean

  quotas?: Record<string, number>
  production: DoubleCountingProduction[]
  setQuotas?: (quotas: Record<string, number>) => void
}

export const ProductionTable = ({
  hasAgreement,

  quotas,
  production,
  setQuotas,
}: ProductionTableProps) => {
  const { t } = useTranslation()

  const productionColumns: Column<DoubleCountingProduction>[] = [
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
    {
      header: t("Quota demandé"),
      cell: (p) => <Cell text={formatNumber(p.requested_quota)} />,
    }
  ]

  hasAgreement && productionColumns?.push({
    header: t("Quota approuvé"),
    cell: (p) => <Cell text={formatNumber(p.approved_quota)} />,
  })

  quotas && setQuotas && productionColumns?.push(
    {
      header: t("Quota approuvé"),
      cell: (p) => <ApprovedQuotasCell production={p} quotas={quotas} setQuotas={setQuotas} />,
    })
  return <YearTable columns={productionColumns} rows={production} />
}

interface ApprovedQuotasCellProps {
  production: DoubleCountingProduction
  quotas: Record<string, number>
  setQuotas: (quotas: Record<string, number>) => void
}
const ApprovedQuotasCell = ({ production, quotas, setQuotas }: ApprovedQuotasCellProps) => {
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
