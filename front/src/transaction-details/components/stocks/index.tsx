import { useNavigate, useLocation, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "../../api"
import { useQuery } from "common-v2/hooks/async"
import useEntity from "carbure/hooks/entity"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Return } from "common-v2/components/icons"
import StockForm from "./stock-form"
import StockTag from "transactions/components/stocks/stock-tag"
import { LoaderOverlay } from "common-v2/components/scaffold"
import NavigationButtons from "transaction-details/components/lots/navigation"
import StockTraceability from "./stock-traceability"
import { SplitOneButton } from "transactions/actions/split"
import { useCategory } from "transactions/components/category"
import { UserRole } from "carbure/types"
import { CancelOneTransformButton } from "transactions/actions/transform-cancel"
import { FlushOneButton } from "transactions/actions/flush-stock"

interface StockDetailsProps {
  neighbors: number[]
}

export const StockDetails = ({ neighbors }: StockDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const category = useCategory()
  const params = useParams<"id">()

  const stock = useQuery(api.getStockDetails, {
    key: "stock-details",
    params: [entity.id, parseInt(params.id!)],
  })

  const hasEditRights = entity.hasRights(UserRole.Admin, UserRole.ReadWrite)

  const stockData = stock.result?.data.data
  const owner = stockData?.stock.carbure_client
  const remaining = stockData?.stock.remaining_volume ?? 0
  const volume = stockData?.stock.initial_volume ?? 0
  const percentLeft = volume > 0 ? (100 * remaining) / volume : 100

  const closeDialog = () =>
    navigate({
      pathname: `../${category}`,
      search: location.search,
    })

  return (
    <Dialog onClose={closeDialog}>
      <header>
        {stockData && <StockTag big stock={stockData.stock} />}
        <h1>
          {t("Détails du stock")} #{stockData?.stock.carbure_id}
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
        {hasEditRights && stockData && stockData.stock.remaining_volume > 0 && (
          <>
            <SplitOneButton stock={stockData.stock} />
            {percentLeft <= 1 && <FlushOneButton stock={stockData.stock} />}
            {stockData.parent_transformation && (
              <CancelOneTransformButton stock={stockData.stock} />
            )}
          </>
        )}
        <NavigationButtons neighbors={neighbors} root={`../${category}`} />
        <Button icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {stock.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default StockDetails
