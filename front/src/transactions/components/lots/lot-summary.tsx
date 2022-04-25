import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common-v2/hooks/async"
import * as api from "../../api"
import { LotQuery, SummaryItem } from "../../types"
import { formatNumber, formatPercentage } from "common-v2/utils/formatters"
import { getDeliveryLabel } from "common-v2/utils/normalizers"
import { toSearchParams } from "common-v2/services/api"
import { usePortal } from "common-v2/components/portal"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Alert from "common-v2/components/alert"
import Button, { ExternalLink } from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import Table, { Cell } from "common-v2/components/table"
import { Filter, Return } from "common-v2/components/icons"
import { FilterManager, ResetButton } from "../filters"
import NoResult from "../no-result"
import { compact } from "common-v2/utils/collection"

export interface LotSummaryBarProps extends Partial<FilterManager> {
  query: LotQuery
  selection: number[]
  getSummary?: typeof api.getLotsSummary
  renderSummary?: typeof LotSummary
}

export const LotSummaryBar = ({
  query,
  selection,
  filters,
  onFilter,
  getSummary = api.getLotsSummary,
  renderSummary = LotSummary,
}: LotSummaryBarProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const summary = useQuery(getSummary, {
    key: "lots-summary",
    params: [query, selection, true],
  })

  const summaryData = summary.result?.data.data ?? { count: 0, total_volume: 0 }

  return (
    <Alert loading={summary.loading} icon={Filter} variant="info">
      <p>
        <Trans count={summaryData.count}>
          <b>{{ count: formatNumber(summaryData.count) }} lots</b> pour un total
          de <b>{{ volume: formatNumber(summaryData.total_volume) }} litres</b>
        </Trans>
      </p>

      <Button
        variant="link"
        label={t("Voir le récapitulatif")}
        action={() =>
          portal((close) => (
            <LotSummaryDialog
              query={query}
              selection={selection}
              onClose={close}
              renderSummary={renderSummary}
              getSummary={getSummary}
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

export interface LotSummaryDialogProps {
  query: LotQuery
  selection: number[]
  onClose: () => void
  renderSummary?: typeof LotSummary
  getSummary?: typeof api.getLotsSummary
}

export const LotSummaryDialog = ({
  query,
  selection,
  onClose,
  renderSummary: Summary = LotSummary,
  getSummary,
}: LotSummaryDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Récapitulatif des lots")}</h1>
      </header>

      <main>
        <section>
          {t(
            "Ce tableau résume les informations principales des lots correspondant à votre recherche ou sélection."
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

export interface LotSummaryProps {
  pending?: boolean
  query: LotQuery
  selection?: number[]
  getSummary?: typeof api.getLotsSummary
}

const EMPTY: number[] = []

export const LotSummary = ({
  pending,
  query,
  selection = EMPTY,
  getSummary = api.getLotsSummary,
}: LotSummaryProps) => {
  const { t } = useTranslation()

  const summary = useQuery(getSummary, {
    key: "lots-summary-details",
    params: [query, selection],
  })

  const columns = useSummaryColumns(query)

  const summaryData = summary.result?.data.data

  const input = summaryData?.in ?? []
  const inputLots = input.reduce((count, item) => count + item.total, 0)
  const inputVolume = input.reduce((volume, item) => volume + item.volume_sum, 0) // prettier-ignore

  const output = summaryData?.out ?? []
  const outputLots = output.reduce((count, item) => count + item.total, 0)
  const outputVolume = output.reduce((volume, item) => volume + item.volume_sum, 0) // prettier-ignore

  return (
    <>
      {input.length === 0 && output.length === 0 && (
        <section>
          <NoResult />
        </section>
      )}

      {input.length > 0 && (
        <>
          <h2>
            {t("Lots reçus")}
            {" ▸ "}
            {t("{{count}} lots", { count: inputLots })}
            {" ▸ "}
            {t("{{volume}} litres", {
              count: inputVolume,
              volume: formatNumber(inputVolume),
            })}
          </h2>
          <Table
            style={{ width: "max(50vw, 960px)" }}
            rows={input}
            columns={compact([
              columns.supplier,
              columns.delivery,
              columns.biofuel,
              columns.volume,
              pending ? columns.countWithPending : columns.count,
              columns.ghgReduction,
              pending && columns.shortcut,
            ])}
          />
        </>
      )}

      {output.length > 0 && (
        <>
          <h2>
            {t("Lots envoyés")}
            {" ▸ "}
            {t("{{count}} lots", { count: outputLots })}
            {" ▸ "}
            {t("{{volume}} litres", {
              count: outputVolume,
              volume: formatNumber(outputVolume),
            })}
          </h2>
          <Table
            rows={output}
            style={{ width: "max(50vw, 960px)" }}
            columns={compact([
              columns.client,
              columns.delivery,
              columns.biofuel,
              columns.volume,
              pending ? columns.countWithPending : columns.count,
              columns.ghgReduction,
              pending && columns.shortcut,
            ])}
          />
        </>
      )}

      {summary.loading && <LoaderOverlay />}
    </>
  )
}

export function useSummaryColumns(query: LotQuery) {
  const { t } = useTranslation()
  return {
    supplier: {
      key: "supplier",
      header: t("Fournisseur"),
      orderBy: (item: SummaryItem) => item.supplier ?? "",
      cell: (item: SummaryItem) => (
        <Cell text={item.supplier ?? t("Inconnu")} />
      ),
    },
    client: {
      key: "client",
      header: t("Client"),
      orderBy: (item: SummaryItem) => item.client ?? "",
      cell: (item: SummaryItem) => <Cell text={item.client ?? t("Inconnu")} />,
    },
    delivery: {
      key: "delivery",
      header: t("Livraison"),
      orderBy: (item: SummaryItem) => item.delivery_type ?? "",
      cell: (item: SummaryItem) => (
        <Cell text={getDeliveryLabel(item.delivery_type)} />
      ),
    },

    biofuel: {
      key: "biofuel",
      header: t("Biocarburant"),
      orderBy: (item: SummaryItem) =>
        t(item.biofuel_code ?? "", { ns: "biofuels" }) as string,
      cell: (item: SummaryItem) => (
        <Cell text={t(item.biofuel_code ?? "", { ns: "biofuels" })} />
      ),
    },
    volume: {
      key: "volume",
      header: t("Volume (litres)"),
      orderBy: (item: SummaryItem) => item.volume_sum,
      cell: (item: SummaryItem) => (
        <Cell text={formatNumber(item.volume_sum)} />
      ),
    },
    remainingVolume: {
      key: "volume",
      header: t("Volume restant (litres)"),
      orderBy: (item: SummaryItem) => item.remaining_volume_sum ?? 0,
      cell: (item: SummaryItem) => (
        <Cell text={formatNumber(item.remaining_volume_sum ?? 0)} />
      ),
    },
    count: {
      small: true,
      key: "lots",
      header: t("Lots"),
      orderBy: (item: SummaryItem) => item.total,
      cell: (item: SummaryItem) => <Cell text={item.total} />,
    },
    countWithPending: {
      small: true,
      key: "lots",
      header: t("Lots validés"),
      orderBy: (item: SummaryItem) => item.total - item.pending,
      cell: (item: SummaryItem) => <PendingCountCell item={item} />,
    },
    ghgReduction: {
      small: true,
      key: "ghg",
      header: t("Réd. GES"),
      orderBy: (item: SummaryItem) => item.avg_ghg_reduction || 0,
      cell: (item: SummaryItem) => (
        <Cell text={formatPercentage(item.avg_ghg_reduction || 0)} />
      ),
    },
    shortcut: {
      small: true,
      header: t("Aperçu"),
      cell: (item: SummaryItem) => (
        <PreviewCell status="out" item={item} query={query} />
      ),
    },
  }
}

interface PendingCountCellProps {
  item: SummaryItem
}

export const PendingCountCell = ({ item }: PendingCountCellProps) => (
  <p
    style={{
      color: item.pending > 0 ? "var(--orange-dark)" : undefined,
    }}
  >
    <strong>{item.total - item.pending}</strong>
    <small> / {item.total}</small>
  </p>
)

interface PreviewCellProps {
  status: "in" | "out"
  item: SummaryItem
  query: LotQuery
}

export const PreviewCell = ({ status, item, query }: PreviewCellProps) => {
  const { t } = useTranslation()

  const filters: Record<string, any> = {
    periods: query.periods,
    biofuels: [item.biofuel_code],
  }

  if (status === "in") {
    filters.suppliers = [item.supplier]
  } else {
    filters.clients = [item.client]
  }

  return (
    <ExternalLink
      href={`../../${query.year}/${status}/history?${toSearchParams(filters)}`}
    >
      {t("Voir")}
    </ExternalLink>
  )
}
