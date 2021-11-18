import { useNavigate, useLocation, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import { useQuery } from "common-v2/hooks/async"
import useEntity from "carbure/hooks/entity"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Return, Save } from "common-v2/components/icons"
import StockForm from "./components/stock-form"
import StockTag from "transactions-v2/components/stock-tag"
import { LoaderOverlay } from "common-v2/components/scaffold"

export const StockDetails = () => {
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

  const closeDialog = () =>
    navigate({
      pathname: `../stocks`,
      search: location.search,
    })

  return (
    <Dialog onClose={closeDialog}>
      <header>
        {stockData && <StockTag big stock={stockData.stock} />}
        <h1>
          {t("Détails du stock")} #{stockData?.stock.id}
        </h1>
      </header>

      <main>
        <section>
          <StockForm
            stock={stockData?.stock}
            onSubmit={(form) => console.log(form)}
          />
        </section>
      </main>

      <footer>
        <Button
          variant="primary"
          icon={Save}
          submit="stock-form"
          label={t("Sauvegarder")}
        />
        <Button asideX icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {stock.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default StockDetails
