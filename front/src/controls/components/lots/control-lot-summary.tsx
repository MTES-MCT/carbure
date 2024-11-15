import { useTranslation } from "react-i18next"
import { useQuery } from "common/hooks/async"
import pickApi from "../../api"
import { formatUnit } from "common/utils/formatters"
import { LoaderOverlay } from "common/components/scaffold"
import Table from "common/components/table"
import NoResult from "common/components/no-result"
import {
  LotSummaryBar,
  LotSummaryBarProps,
  LotSummaryProps,
  useSummaryColumns,
} from "transactions/components/lots/lot-summary"
import useEntity from "carbure/hooks/entity"
import { compact } from "common/utils/collection"
import { Unit } from "carbure/types"

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

  const summaryData = summary.result?.data
  
  const unitToField = {
    l: "volume_sum" as const,
    kg: "weight_sum" as const,
    MJ: "lhv_amount_sum" as const,
  }

  const unit = entity.preferred_unit ?? Unit.l
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
              columns.quantity,
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
