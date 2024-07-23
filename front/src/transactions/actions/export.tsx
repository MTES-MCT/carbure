import { useTranslation } from "react-i18next"
import { LotQuery, StockQuery } from "../types"
import { Download } from "common/components/icons"
import Button from "common/components/button"
import * as api from "../api"
import { useMatomo } from "matomo"

export interface ExportLotsButtonProps {
	asideX?: boolean
	query: LotQuery
	selection: number[]
}

export const ExportLotsButton = ({
	asideX,
	query,
	selection,
}: ExportLotsButtonProps) => {
	const matomo = useMatomo()
	const { t } = useTranslation()
	return (
		<Button
			asideX={asideX}
			icon={Download}
			label={t("Exporter vers Excel")}
			action={() => {
				matomo.push([
					"trackEvent",
					"lots",
					"export-lots-excel",
					selection.length,
				])
				api.downloadLots(query, selection)
			}}
		/>
	)
}

export interface ExportStockButtonProps {
	asideX?: boolean
	query: StockQuery
	selection: number[]
}

export const ExportStocksButton = ({
	asideX,
	query,
	selection,
}: ExportStockButtonProps) => {
	const matomo = useMatomo()
	const { t } = useTranslation()
	return (
		<Button
			asideX={asideX}
			icon={Download}
			label={t("Exporter vers Excel")}
			action={() => {
				matomo.push([
					"trackEvent",
					"stocks",
					"export-stocks-excel",
					selection.length,
				])
				api.downloadStocks(query, selection)
			}}
		/>
	)
}
