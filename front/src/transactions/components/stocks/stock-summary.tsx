import { Trans, useTranslation } from "react-i18next"
import * as api from "../../api"
import { StockQuery } from "../../types"
import { useQuery } from "common/hooks/async"
import { usePortal } from "common/components/portal"
import { formatNumber, formatUnit } from "common/utils/formatters"
import { LoaderOverlay } from "common/components/scaffold"
import Alert from "common/components/alert"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import Table from "common/components/table"
import { Filter, Return } from "common/components/icons"
import { FilterManager, ResetButton } from "../filters"
import NoResult from "../../../common/components/no-result"
import { useSummaryColumns } from "../lots/lot-summary"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"

export interface StockSummaryBarProps extends Partial<FilterManager> {
  query: StockQuery
  selection: number[]
  getSummary?: typeof api.getStockSummary
  renderSummary?: typeof StockSummary
}

export const StockSummaryBar = ({
  query,
  selection,
  filters,
  onFilter,
  getSummary = api.getStockSummary,
  renderSummary = StockSummary,
}: StockSummaryBarProps) => {
  const { t } = useTranslation()
  const portal = usePortal()
  const entity = useEntity()

  const summary = useQuery(getSummary, {
    key: "stock-summary",
    params: [query, selection, true],
  })

  const summaryData = summary.result?.data.data ?? {
    count: 0,
    total_remaining_volume: 0,
    total_remaining_weight: 0,
    total_remaining_lhv_amount: 0,
  }

  const unitToField = {
    l: "total_remaining_volume" as "total_remaining_volume",
    kg: "total_remaining_weight" as "total_remaining_weight",
    MJ: "total_remaining_lhv_amount" as "total_remaining_lhv_amount",
  }

  const unit = entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  return (
    <Alert loading={summary.loading} icon={Filter} variant="info">
      <p>
        <Trans
          defaults="<b>{{amount}} stocks</b> pour un total de <b>{{volume}} restants</b>"
          count={summaryData.count}
          values={{
            amount: formatNumber(summaryData.count),
            volume: formatUnit(summaryData[field], unit),
          }}
        />
      </p>

      <Button
        variant="link"
        label={t("Voir le récapitulatif")}
        action={() =>
          portal((close) => (
            <StockSummaryDialog
              query={query}
              selection={selection}
              onClose={close}
              getSummary={getSummary}
              renderSummary={renderSummary}
            />
          ))
        }
      />

      {filters && onFilter && (
        <ResetButton filters={filters} onFilter={onFilter} />
      )}
    </Alert>
  )
}

export interface StockSummaryDialogProps {
  query: StockQuery
  selection: number[]
  onClose: () => void
  getSummary?: typeof api.getStockSummary
  renderSummary?: typeof StockSummary
}

export const StockSummaryDialog = ({
  query,
  selection,
  onClose,
  getSummary,
  renderSummary: Summary = StockSummary,
}: StockSummaryDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Récapitulatif des lots")}</h1>
      </header>

      <main>
        <section>
          {t(
            "Ce tableau résume les informations principales des stocks correspondant à votre recherche ou sélection."
          )}
        </section>

        <Summary query={query} selection={selection} getSummary={getSummary} />
      </main>

      <footer>
        <Button asideX icon={Return} label={t("Retour")} action={onClose} />
      </footer>
    </Dialog>
  )
}

export interface StockSummaryProps {
  query: StockQuery
  selection?: number[]
  getSummary?: typeof api.getStockSummary
}

const EMPTY: number[] = []

export const StockSummary = ({
  query,
  selection = EMPTY,
  getSummary = api.getStockSummary,
}: StockSummaryProps) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const summary = useQuery(getSummary, {
    key: "stocks-summary-details",
    params: [query, selection],
  })

  const summaryData = summary.result?.data.data

  const unitToField = {
    l: "remaining_volume_sum" as "remaining_volume_sum",
    kg: "remaining_weight_sum" as "remaining_weight_sum",
    MJ: "remaining_lhv_amount_sum" as "remaining_lhv_amount_sum",
  }

  const unit = entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  const stock = summaryData?.stock ?? []
  const stockLots = stock.reduce((count, item) => count + item.total, 0)
  const stockQuantity = stock.reduce((quantity, item) => quantity + (item[field] ?? 0), 0) // prettier-ignore

  const columns = useSummaryColumns(query)

  return (
    <>
      {stock.length === 0 && (
        <section>
          <NoResult />
        </section>
      )}

      {stock.length > 0 && (
        <>
          <h2>
            {t("Stocks")}
            {" ▸ "}
            {t("{{count}} lots", { count: stockLots })}
            {" ▸ "}
            {formatUnit(stockQuantity, unit)}
          </h2>
          <Table
            style={{ width: "max(50vw, 960px)" }}
            rows={stock}
            columns={compact([
              columns.supplier,
              columns.biofuel,
              columns.remainingQuantity,
              columns.count,
              columns.ghgReduction,
            ])}
          />
        </>
      )}

      {summary.loading && <LoaderOverlay />}
    </>
  )
}
