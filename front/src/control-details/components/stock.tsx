import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import pickApi from "../api"
import { useQuery } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { LoaderOverlay } from "common/components/scaffold"
import Dialog from "common/components/dialog"
import StockTag from "transactions/components/stocks/stock-tag"
import NavigationButtons from "transaction-details/components/lots/navigation"

import StockForm from "transaction-details/components/stocks/stock-form"
import StockTraceability, {
  hasTraceability,
} from "transaction-details/components/stocks/stock-traceability"
import Portal from "common/components/portal"
import { useHashMatch } from "common/components/hash-route"

export interface StockDetailsProps {
  neighbors: number[]
}

export const StockDetails = ({ neighbors }: StockDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const match = useHashMatch("stock/:id")

  const api = pickApi(entity)

  const stock = useQuery(api.getStockDetails, {
    key: "control-stock-details",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const stockData = stock.result?.data.data
  const creator = stockData?.stock.carbure_client

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  return (
    <Portal onClose={closeDialog}>
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
                parentLotRoot="../lots"
                parentTransfoRoot="../stocks"
                childLotRoot="../lots"
                childTransfoRoot="../stocks"
              />
            </section>
          )}
        </main>

        <footer>
          <NavigationButtons neighbors={neighbors} closeAction={closeDialog} />
        </footer>

        {stock.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default StockDetails
