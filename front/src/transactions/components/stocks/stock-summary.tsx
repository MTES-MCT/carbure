import { Trans, useTranslation } from "react-i18next"
import * as api from "../../api"
import { StockQuery } from "../../types"
import { useQuery } from "common-v2/hooks/async"
import { usePortal } from "common-v2/components/portal"
import { formatNumber, formatPercentage } from "common-v2/utils/formatters"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Alert from "common-v2/components/alert"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import Table, { Cell } from "common-v2/components/table"
import { Filter, Return } from "common-v2/components/icons"
import { FilterManager, ResetButton } from "../filters"
import NoResult from "../no-result"

export interface StockSummaryBarProps extends Partial<FilterManager> {
  query: StockQuery
  selection: number[]
}

export const StockSummaryBar = ({
  query,
  selection,
  filters,
  onFilter,
}: StockSummaryBarProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const summary = useQuery(api.getStockSummary, {
    key: "stock-summary",
    params: [query, selection, true],
  })

  const summaryData = summary.result?.data.data ?? {
    count: 0,
    total_remaining_volume: 0,
  }

  return (
    <Alert loading={summary.loading} icon={Filter} variant="info">
      <p>
        <Trans count={summaryData.count}>
          <b>{{ count: formatNumber(summaryData.count) }} stocks</b> pour un
          total de{" "}
          <b>
            {{ volume: formatNumber(summaryData.total_remaining_volume) }}{" "}
            litres restants
          </b>
        </Trans>
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
}

export const StockSummaryDialog = ({
  query,
  selection,
  onClose,
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

        <StockSummary query={query} selection={selection} />
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
}

const EMPTY: number[] = []

export const StockSummary = ({
  query,
  selection = EMPTY,
}: StockSummaryProps) => {
  const { t } = useTranslation()

  const summary = useQuery(api.getStockSummary, {
    key: "stocks-summary-details",
    params: [query, selection],
  })

  const summaryData = summary.result?.data.data

  const stock = summaryData?.stock ?? []
  const stockLots = stock.reduce((count, item) => count + item.total, 0)
  const stockVolume = stock.reduce((volume, item) => volume + (item.remaining_volume_sum ?? 0), 0) // prettier-ignore

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
            <Trans>
              Entrées ▸ {{ lots: formatNumber(stockLots) }} lots ▸{" "}
              {{ volume: formatNumber(stockVolume) }} litres
            </Trans>
          </h2>
          <Table
            rows={stock}
            columns={[
              {
                key: "supplier",
                header: t("Fournisseur"),
                orderBy: (item) => item.supplier ?? "",
                cell: (item) => <Cell text={item.supplier ?? t("Inconnu")} />,
              },
              {
                key: "biofuel",
                header: t("Biocarburant"),
                orderBy: (item) => item.biofuel_code ?? "",
                cell: (item) => (
                  <Cell text={t(item.biofuel_code ?? "", { ns: "biofuels" })} />
                ),
              },
              {
                key: "volume",
                header: t("Volume restant (litres)"),
                orderBy: (item) => item.remaining_volume_sum ?? 0,
                cell: (item) => (
                  <Cell text={formatNumber(item.remaining_volume_sum ?? 0)} />
                ),
              },
              {
                small: true,
                key: "lots",
                header: t("Lots"),
                orderBy: (item) => item.total,
                cell: (item) => <Cell text={item.total} />,
              },
              {
                small: true,
                key: "ghg",
                header: t("Réd. GES"),
                orderBy: (item) => item.avg_ghg_reduction || 0,
                cell: (item) => (
                  <Cell text={formatPercentage(item.avg_ghg_reduction || 0)} />
                ),
              },
            ]}
          />
        </>
      )}

      {summary.loading && <LoaderOverlay />}
    </>
  )
}
