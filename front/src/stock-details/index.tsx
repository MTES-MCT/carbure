import { useNavigate, useLocation, useParams } from "react-router-dom"
import { Trans, useTranslation } from "react-i18next"
import * as api from "./api"
import { useQuery } from "common-v2/hooks/async"
import useEntity from "carbure/hooks/entity"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { AlertCircle, Return } from "common-v2/components/icons"
import StockForm from "./components/stock-form"
import StockTag from "transactions/components/stocks/stock-tag"
import { LoaderOverlay } from "common-v2/components/scaffold"
import NavigationButtons from "lot-details/components/navigation"
import Alert from "common-v2/components/alert"
import { formatNumber, formatPercentage } from "common-v2/utils/formatters"
import StockTraceability from "./components/stock-traceability"
import { SplitOneButton } from "transactions/actions/split"

interface StockDetailsProps {
  neighbors: number[]
}

export const StockDetails = ({ neighbors }: StockDetailsProps) => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const params = useParams<"id">()

  const stock = useQuery(api.getStockDetails, {
    key: "stock-details",
    params: [entity.id, parseInt(params.id!)],
  })

  const stockData = stock.result?.data.data
  const remaining = stockData?.stock.remaining_volume ?? 0
  const volume = stockData?.stock.initial_volume ?? 0
  const percent = (100 * remaining) / (volume || 1)

  const closeDialog = () =>
    navigate({
      pathname: `..`,
      search: location.search,
    })

  return (
    <Dialog onClose={closeDialog}>
      <header>
        {stockData && <StockTag big stock={stockData.stock} />}
        <h1>
          {t("Détails du stock")} #{stockData?.stock.carbure_id}
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
        {stockData && <SplitOneButton stock={stockData?.stock} />}
        <Alert icon={AlertCircle} variant="info">
          <p>
            <Trans>
              <b>{{ remaining: formatNumber(remaining) }} litres restants</b> (
              {{ percent: formatPercentage(percent) }})
            </Trans>
          </p>
        </Alert>
        <NavigationButtons neighbors={neighbors} root=".." />
        <Button icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {stock.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default StockDetails
