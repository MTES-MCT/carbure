import Checkbox from "common/components/checkbox"
import { Cell, Column } from "common/components/table"
import { formatNumber } from "common/utils/formatters"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import {
	DoubleCountingProduction,
	DoubleCountingSourcing,
	DoubleCountingSourcingAggregation,
} from "../types"
import YearTable from "./year-table"

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
			cell: (s) =>
				s.origin_country?.code_pays ? (
					<Cell text={t(s.origin_country.code_pays, { ns: "countries" })} />
				) : null,
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
				) : (
					"-"
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
	]

	return <YearTable columns={columns} rows={sourcing} />
}

export const SourcingFullTable = ({
	sourcing,
}: {
	sourcing: DoubleCountingSourcing[]
}) => {
	const [aggregateSourcing, setAggregateSourcing] = useState(true)
	const { t } = useTranslation()

	const aggregateDoubleCountingSourcing = (
		data: DoubleCountingSourcing[]
	): DoubleCountingSourcingAggregation[] => {
		const aggregationMap = new Map<string, DoubleCountingSourcingAggregation>()
		for (const item of data) {
			const key = `${item.feedstock.code}_${item.year}`
			const aggregation = aggregationMap.get(key)

			if (aggregation) {
				aggregation.sum += item.metric_tonnes
				aggregation.count += 1
			} else {
				aggregationMap.set(key, {
					year: item.year,
					sum: item.metric_tonnes,
					count: 1,
					feedstock: item.feedstock,
				})
			}
		}

		return Array.from(aggregationMap.values())
	}

	const aggregated_sourcing: DoubleCountingSourcingAggregation[] =
		aggregateDoubleCountingSourcing(sourcing)

	return (
		<>
			{sourcing?.length > 0 && (
				<Checkbox
					readOnly
					value={aggregateSourcing}
					onChange={() => setAggregateSourcing(!aggregateSourcing)}
				>
					{t("Agréger les données d'approvisionnement par matière première")}
				</Checkbox>
			)}
			{!aggregateSourcing && <SourcingTable sourcing={sourcing ?? []} />}
			{aggregateSourcing && (
				<SourcingAggregationTable sourcing={aggregated_sourcing ?? []} />
			)}
		</>
	)
}

type ProductionTableProps = {
	hasAgreement?: boolean

	quotas?: Record<string, number>
	production: DoubleCountingProduction[]
	setQuotas?: (quotas: Record<string, number>) => void
}
