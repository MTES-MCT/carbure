import { useTranslation } from "react-i18next"
import { Entity, EntityType } from "carbure/types"
import {
  Admin,
  DoubleCountingSourcing,
  DoubleCountingProduction,
  DoubleCountingDetails,
  DoubleCountingSourcingAggregation,
} from "../types"
import Table, { Column, Cell } from "common/components/table"
import { NumberInput } from "common/components/input"
import YearTable from "./year-table"
import { formatDate, formatNumber } from "common/utils/formatters"
import Checkbox from "common/components/checkbox"
import { useState } from "react"

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
        s.transit_country && (
          <Cell text={t(s.transit_country.code_pays, { ns: "countries" })} />
        ),
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
    },
    {
      header: t("Pays d'origine"),
      cell: (s) => <Cell text={s.count} />,
    },
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

    <Checkbox readOnly value={aggregateSourcing} onChange={() => setAggregateSourcing(!aggregateSourcing)}>
      {t("Agréger les données d’approvisionnement par matière première")}
    </Checkbox>
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
  done?: boolean
  entity?: Entity
  quotas?: Record<string, number>
  production: DoubleCountingProduction[]
  setQuotas?: (quotas: Record<string, number>) => void
}

export const ProductionTable = ({
  done,
  entity,
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
    },

  ]
  quotas && setQuotas && productionColumns?.push(
    {
      header: t("Quota approuvé"),
      cell: (p) => {
        if (done || entity?.entity_type !== EntityType.Administration) {
          return p.approved_quota >= 0 ? p.approved_quota : p.requested_quota
        }

        return (
          <NumberInput
            value={quotas[p.id]}
            onChange={(value) =>
              setQuotas({
                ...quotas,
                [p.id]: value,
              })
            }
          />
        )
      }
    })
  return <YearTable columns={productionColumns} rows={production} />
}

type StatusTableProps = {
  agreement: DoubleCountingDetails | undefined
}

export const StatusTable = ({ agreement }: StatusTableProps) => {
  const { t } = useTranslation()

  const statusColumns: Column<ValidationStatus>[] = [
    {
      header: t("Administration"),
      cell: (s) => <Cell text={s.entity} />,
    },
    {
      header: t("Statut"),
      cell: (s) => (
        <Cell
          text={
            !s.approved && s.user
              ? t("Refusé")
              : s.approved
                ? t("Accepté")
                : t("En attente")
          }
        />
      ),
    },
    {
      header: t("Validateur"),
      cell: (s) => <Cell text={s.user} />,
    },
    {
      header: t("Date"),
      cell: (s) => <Cell text={formatDate(s.date)} />,
    },
  ]

  const statusRows: ValidationStatus[] = [
    {
      approved: agreement?.dgec_validated ?? false,
      date: agreement?.dgec_validated_dt ?? "",
      user: agreement?.dgec_validator ?? "",
      entity: Admin.DGEC,
    },
    {
      approved: agreement?.dgddi_validated ?? false,
      date: agreement?.dgddi_validated_dt ?? "",
      user: agreement?.dgddi_validator ?? "",
      entity: Admin.DGDDI,
    },
    {
      approved: agreement?.dgpe_validated ?? false,
      date: agreement?.dgpe_validated_dt ?? "",
      user: agreement?.dgpe_validator ?? "",
      entity: Admin.DGPE,
    },
  ]

  return <Table columns={statusColumns} rows={statusRows} />
}
