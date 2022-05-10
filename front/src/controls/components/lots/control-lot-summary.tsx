import { useTranslation } from "react-i18next"
import { useQuery } from "common-v2/hooks/async"
import pickApi from "../../api"
import { formatNumber } from "common-v2/utils/formatters"
import { LoaderOverlay } from "common-v2/components/scaffold"
import Table from "common-v2/components/table"
import NoResult from "transactions/components/no-result"
import {
  LotSummaryBar,
  LotSummaryBarProps,
  LotSummaryProps,
  useSummaryColumns,
} from "transactions/components/lots/lot-summary"
import useEntity from "carbure/hooks/entity"

export const ControlLotSummaryBar = (props: LotSummaryBarProps) => {
  const entity = useEntity()
  const api = pickApi(entity)

  return (
    <LotSummaryBar
      {...props}
      getSummary={api.getLotsSummary}
      renderSummary={ControlLotSummary}
    />
  )
}

const EMPTY: number[] = []

export const ControlLotSummary = ({
  query,
  selection = EMPTY,
}: LotSummaryProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const api = pickApi(entity)

  const summary = useQuery(api.getLotsSummary, {
    key: "lots-summary-details",
    params: [query, selection],
  })

  const summaryData = summary.result?.data.data
  const lots = summaryData?.lots ?? []
  const lotsAmount = lots.reduce((count, item) => count + item.total, 0)
  const lotsVolume = lots.reduce((volume, item) => volume + item.volume_sum, 0) // prettier-ignore

  const columns = useSummaryColumns(query)

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

          <Table
            style={{ width: "max(50vw, 960px)" }}
            rows={lots}
            columns={[
              columns.supplier,
              columns.client,
              columns.delivery,
              columns.biofuel,
              columns.volume,
              columns.count,
              columns.ghgReduction,
            ]}
          />
        </>
      )}

      {summary.loading && <LoaderOverlay />}
    </>
  )
}
