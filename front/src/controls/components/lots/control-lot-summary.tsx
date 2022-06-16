import { useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import pickApi from "../../api"
import { formatNumber, formatUnit } from "common/utils/formatters"
import { LoaderOverlay } from "common/components/scaffold"
import Table from "common/components/table"
import NoResult from "transactions/components/no-result"
import {
  LotSummaryBar,
  LotSummaryBarProps,
  LotSummaryProps,
  useSummaryColumns,
} from "transactions/components/lots/lot-summary"
import useEntity from "carbure/hooks/entity"
import Flags from "flags.json"
import { compact } from "common/utils/collection"

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

  const unitToField = {
    l: "volume_sum" as "volume_sum",
    kg: "weight_sum" as "weight_sum",
    MJ: "lhv_amount_sum" as "lhv_amount_sum",
  }

  const unit = !Flags.preferred_unit ? "l" : entity.preferred_unit ?? "l"
  const field = unitToField[unit]

  const lots = summaryData?.lots ?? []
  const lotsAmount = lots.reduce((count, item) => count + item.total, 0)
  const lotsQuantity = lots.reduce((quantity, item) => quantity + item[field], 0) // prettier-ignore

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
            {formatUnit(lotsQuantity, unit)}
          </h2>

          <Table
            style={{ width: "max(50vw, 960px)" }}
            rows={lots}
            columns={compact([
              columns.supplier,
              columns.client,
              columns.delivery,
              columns.biofuel,
              !Flags.preferred_unit && columns.volume,
              Flags.preferred_unit && columns.quantity,
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
