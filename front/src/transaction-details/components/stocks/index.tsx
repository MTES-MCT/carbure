import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "../../api"
import { useQuery } from "common/hooks/async"
import useEntity from "carbure/hooks/entity"
import Dialog from "common/components/dialog"
import StockForm from "./stock-form"
import StockTag from "transactions/components/stocks/stock-tag"
import { LoaderOverlay } from "common/components/scaffold"
import NavigationButtons from "transaction-details/components/lots/navigation"
import StockTraceability from "./stock-traceability"
import { SplitOneButton } from "transactions/actions/split"
import { UserRole } from "carbure/types"
import { CancelOneTransformButton } from "transactions/actions/transform-cancel"
import { FlushOneButton } from "transactions/actions/flush-stock"
import Portal from "common/components/portal"
import { useHashMatch } from "common/components/hash-route"

interface StockDetailsProps {
  neighbors: number[]
}

export const StockDetails = ({ neighbors }: StockDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const match = useHashMatch("stock/:id")

  const stock = useQuery(api.getStockDetails, {
    key: "stock-details",
    params: [entity.id, parseInt(match?.params.id || "")],
  })

  const hasEditRights = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)

  const stockData = stock.result?.data.data
  const owner = stockData?.stock.carbure_client
  const remaining = stockData?.stock.remaining_volume ?? 0
  const volume = stockData?.stock.initial_volume ?? 0
  const percentLeft = volume > 0 ? (100 * remaining) / volume : 100

  const closeDialog = () => navigate({ search: location.search, hash: "#" })

  return (
    <Portal onClose={closeDialog}>
      <Dialog onClose={closeDialog}>
        <header>
          {stockData && <StockTag big stock={stockData.stock} />}
          <h1>
            {t("Stock")} #{stockData?.stock.carbure_id}
            {" · "}
            {owner?.name ?? "N/A"}
          </h1>
        </header>

        <main>
          <section>
            <StockForm stock={stockData?.stock} />
          </section>

          <section>
            <StockTraceability details={stockData} />
          </section>
        </main>

        <footer>
          {hasEditRights &&
            stockData &&
            stockData.stock.remaining_volume > 0 && (
              <>
                <SplitOneButton stock={stockData.stock} />
                {percentLeft <= 5 && <FlushOneButton stock={stockData.stock} />}
                {stockData.parent_transformation && (
                  <CancelOneTransformButton stock={stockData.stock} />
                )}
              </>
            )}
          <NavigationButtons neighbors={neighbors} closeAction={closeDialog} />
        </footer>

        {stock.loading && <LoaderOverlay />}
      </Dialog>
    </Portal>
  )
}

export default StockDetails
