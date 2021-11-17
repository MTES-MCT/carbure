import { useNavigate, useLocation, useParams } from "react-router-dom"
import { useTranslation } from "react-i18next"
import * as api from "./api"
import { useQuery } from "common-v2/hooks/async"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Return, Save } from "common-v2/components/icons"
import LotForm from "transaction-add/components/form"
import useStatus from "transactions-v2/hooks/status"
import useEntity from "carbure/hooks/entity"
import { LoaderOverlay } from "common-v2/components/scaffold"

export const TransactionDetails = () => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const entity = useEntity()
  const status = useStatus()
  const params = useParams<"id">()

  const lot = useQuery(api.getLotDetails, {
    key: "lot-details",
    params: [entity.id, parseInt(params.id!)],
  })

  const lotData = lot.result?.data.data

  const closeDialog = () =>
    navigate({
      pathname: `../${status}`,
      search: location.search,
    })

  return (
    <Dialog onClose={closeDialog}>
      <header>
        <h1>{t("Détails du lot")}</h1>
      </header>

      <main>
        <section>
          <LotForm lot={lotData?.lot} onSubmit={(form) => console.log(form)} />
        </section>
      </main>

      <footer>
        <Button
          variant="primary"
          icon={Save}
          submit="lot-form"
          label={t("Sauvegarder")}
        />
        <Button asideX icon={Return} label={t("Retour")} action={closeDialog} />
      </footer>

      {lot.loading && <LoaderOverlay />}
    </Dialog>
  )
}

export default TransactionDetails
