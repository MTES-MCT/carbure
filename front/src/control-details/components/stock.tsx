import { useNavigate, useLocation, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import pickApi from "../api"
import { useQuery } from "common/hooks/async"
import { useStatus } from "controls/components/status"
import useEntity from "carbure/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"
import Dialog from "common/components/dialog"
import Button from "common/components/button"
import { Return } from "common/components/icons"
import StockTag from "transactions/components/stocks/stock-tag"
import NavigationButtons from "transaction-details/components/lots/navigation"

import { invalidate } from "common/hooks/invalidate"
import StockForm from "transaction-details/components/stocks/stock-form"
import StockTraceability, {
  hasTraceability,
} from "transaction-details/components/stocks/stock-traceability"

export interface StockDetailsProps {
  neighbors: number[]
}

export const StockDetails = ({ neighbors }: StockDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const status = useStatus()
  const params = useParams<"id">()

  const api = pickApi(entity)

  const stock = useQuery(api.getStockDetails, {
    key: "control-stock-details",
    params: [entity.id, parseInt(params.id!)],
  })

  const stockData = stock.result?.data.data
  const creator = stockData?.stock.carbure_client

  const closeDialog = () => {
    invalidate("controls", "controls-snapshot", "controls-summary")
    navigate({
      pathname: `..`,
      search: location.search,
    })
  }

  return (
    <Dialog onClose={closeDialog}>
      <header>
        {stockData && <StockTag big stock={stockData.stock} />}
        <h1>
          {t("Stock")} #{stockData?.stock.carbure_id || stockData?.stock.id}
          {" · "}
          {creator?.name ?? "N/A"}
        </h1>
      </header>

      <main>
        <section>
          <StockForm stock={stockData?.stock} />
        </section>

        {hasTraceability(stockData) && (
          <section>
            <StockTraceability
              details={stockData}
              parentLotRoot="../../declarations/"
              parentTransfoRoot="../../stocks/"
              childLotRoot="../../declarations/"
              childTransfoRoot="../../stocks/"
            />
          </section>
        )}
      </main>

      <footer>
        <NavigationButtons neighbors={neighbors} root={`..`} />
        <Button icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {stock.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default StockDetails
