import { Trans, useTranslation } from "react-i18next"
import { useQuery } from "common-v2/hooks/async"
import * as api from "../api"
import { LotQuery, SummaryItem } from "transactions/types"
import { formatNumber, formatPercentage } from "common-v2/utils/formatters"
import { usePortal } from "common-v2/components/portal"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Alert from "common-v2/components/alert"
import Button from "common-v2/components/button"
import Dialog from "common-v2/components/dialog"
import Table, { Cell, Column } from "common-v2/components/table"
import { Filter, Return } from "common-v2/components/icons"
import { FilterManager, ResetButton } from "transactions/components/filters"
import NoResult from "transactions/components/no-result"
import { LotCell } from "transactions/components/lots/lot-summary"

export interface LotSummaryBarProps extends Partial<FilterManager> {
  query: LotQuery
  selection: number[]
}

export const LotSummaryBar = ({
  query,
  selection,
  filters,
  onFilter,
}: LotSummaryBarProps) => {
  const { t } = useTranslation()
  const portal = usePortal()

  const summary = useQuery(api.getLotsSummary, {
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
}

export const LotSummaryDialog = ({
  query,
  selection,
  onClose,
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

        <LotSummary query={query} selection={selection} />
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
}

const EMPTY: number[] = []

export const LotSummary = ({
  pending,
  query,
  selection = EMPTY,
}: LotSummaryProps) => {
  const { t } = useTranslation()

  const summary = useQuery(api.getLotsSummary, {
    key: "lots-summary-details",
    params: [query, selection],
  })

  const columns: Column<SummaryItem>[] = [
    {
      key: "supplier",
      header: t("Fournisseur"),
      orderBy: (item) => item.supplier ?? "",
      cell: (item) => <Cell text={item.supplier ?? t("Inconnu")} />,
    },
    {
      key: "client",
      header: t("Client"),
      orderBy: (item) => item.client ?? "",
      cell: (item) => <Cell text={item.client ?? t("Inconnu")} />,
    },
    {
      key: "biofuel",
      header: t("Biocarburant"),
      orderBy: (item) =>
        t(item.biofuel_code ?? "", { ns: "biofuels" }) as string,
      cell: (item) => (
        <Cell text={t(item.biofuel_code ?? "", { ns: "biofuels" })} />
      ),
    },
    {
      key: "volume",
      header: t("Volume (litres)"),
      orderBy: (item) => item.volume_sum,
      cell: (item) => <Cell text={formatNumber(item.volume_sum)} />,
    },
    {
      small: true,
      key: "lots",
      header: pending ? t("Lots validés") : t("Lots"),
      orderBy: (item) => (pending ? item.total - item.pending : item.total),
      cell: (item) => <LotCell pending={pending} item={item} />,
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
  ]

  const summaryData = summary.result?.data.data

  const lots = summaryData?.lots ?? []
  const lotsAmount = lots.reduce((count, item) => count + item.total, 0)
  const lotsVolume = lots.reduce((volume, item) => volume + item.volume_sum, 0) // prettier-ignore

  return (
    <>
      {lots.length === 0 && (
        <section>
          <NoResult />
        </section>
      )}

      {lots.length > 0 && (
        <>
          <h2>
            {t("Transactions")}
            {" ▸ "}
            {t("{{count}} lots", { count: lotsAmount })}
            {" ▸ "}
            {t("{{volume}} litres", {
              count: lotsVolume,
              volume: formatNumber(lotsVolume),
            })}
          </h2>
          <Table rows={lots} columns={[...columns]} />
        </>
      )}

      {summary.loading && <LoaderOverlay />}
    </>
  )
}
