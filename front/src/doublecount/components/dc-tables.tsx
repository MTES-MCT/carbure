import { useTranslation } from "react-i18next"
import { EntityType } from "common/types"
import {
  Admin,
  DoubleCountingSourcing,
  DoubleCountingProduction,
  DoubleCountingDetails,
  DoubleCountingSourcingAggregation,
} from "../types"
import Table, { Column, Line, Row } from "common/components/table"
import { Input } from "common/components/input"
import { padding } from "transactions/components/list-columns"
import { EntitySelection } from "carbure/hooks/use-entity"
import { formatDate } from "settings/components/common"
import YearTable from "./year-table"

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
    padding,
    {
      header: t("Matière première"),
      render: (s) => t(s.feedstock.code, { ns: "feedstocks" }),
    },
    {
      header: t("Poids en tonnes"),
      render: (s) => s.metric_tonnes,
    },
    {
      header: t("Origine"),
      render: (s) => t(s.origin_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Approvisionnement"),
      render: (s) =>
        s.supply_country && t(s.supply_country.code_pays, { ns: "countries" }),
    },
    {
      header: t("Transit"),
      render: (s) =>
        s.transit_country &&
        t(s.transit_country.code_pays, { ns: "countries" }),
    },
    padding,
  ]

  const rows = sourcing.map((v) => ({ value: v }))

  return <YearTable columns={columns} rows={rows} />
}

type SourcingAggregationTableProps = {
  sourcing: DoubleCountingSourcingAggregation[]
}

export const SourcingAggregationTable = ({
  sourcing,
}: SourcingAggregationTableProps) => {
  const { t } = useTranslation()

  const columns: Column<DoubleCountingSourcingAggregation>[] = [
    padding,
    {
      header: t("Matière première"),
      render: (s) => <Line text={t(s.feedstock.code, { ns: "feedstocks" })} />,
    },
    {
      header: t("Poids total en tonnes"),
      render: (s) => <Line text={s.sum} />,
    },
    {
      header: t("Pays d'origine"),
      render: (s) => <Line text={s.count} />,
    },
    padding,
  ]

  const rows = sourcing.map((v) => ({ value: v }))

  return <YearTable columns={columns} rows={rows} />
}

type ProductionTableProps = {
  done?: boolean
  entity: EntitySelection
  quotas: Record<string, string>
  production: DoubleCountingProduction[]
  setQuotas: (quotas: Record<string, string>) => void
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
    padding,
    {
      header: t("Matière première"),
      render: (p) => <Line text={t(p.feedstock.code, { ns: "feedstocks" })} />,
    },
    {
      header: t("Biocarburant"),
      render: (p) => <Line text={t(p.biofuel.code, { ns: "biofuels" })} />,
    },
    {
      header: t("Prod. max"),
      render: (p) => <Line text={p.max_production_capacity} />,
    },
    {
      header: t("Prod. estimée"),
      render: (p) => <Line text={p.estimated_production} />,
    },
    {
      header: t("Quota demandé"),
      render: (p) => <Line text={p.requested_quota} />,
    },
    {
      header: t("Quota approuvé"),
      render: (p) => {
        if (done || entity?.entity_type !== EntityType.Administration) {
          return p.approved_quota >= 0 ? p.approved_quota : p.requested_quota
        }

        return (
          <Input
            value={quotas[p.id]}
            onChange={(e) =>
              setQuotas({
                ...quotas,
                [p.id]: e.target.value,
              })
            }
          />
        )
      },
    },
    padding,
  ]

  const rows = production.map((v) => ({ value: v }))

  return <YearTable columns={productionColumns} rows={rows} />
}

type StatusTableProps = {
  agreement: DoubleCountingDetails | null
}

export const StatusTable = ({ agreement }: StatusTableProps) => {
  const { t } = useTranslation()

  const statusColumns: Column<ValidationStatus>[] = [
    padding,
    {
      header: t("Administration"),
      render: (s) => <Line text={s.entity} />,
    },
    {
      header: t("Statut"),
      render: (s) => (
        <Line
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
      render: (s) => <Line text={s.user} />,
    },
    {
      header: t("Date"),
      render: (s) => <Line text={formatDate(s.date)} />,
    },
    padding,
  ]

  const statusRows: Row<ValidationStatus>[] = [
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
  ].map((value) => ({ value }))

  return <Table columns={statusColumns} rows={statusRows} />
}
