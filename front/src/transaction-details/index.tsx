import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import Dialog from "common-v2/components/dialog"
import Button from "common-v2/components/button"
import { Return, Save } from "common-v2/components/icons"
import LotForm from "transaction-add/components/form"
import useStatus from "transactions-v2/hooks/status"

export const TransactionDetails = () => {
  const { t } = useTranslation()

  const status = useStatus()
  const location = useLocation()
  const navigate = useNavigate()

  const close = () => navigate({
    pathname: `../${status}`,
    search: location.search
  })

  return (
    <Dialog onClose={close}>
      <header>
        <h1>{t("Détails du lot")}</h1>
      </header>

      <main>
        <section>
          <LotForm onSubmit={(form) => console.log(form)} />
        </section>
      </main>

      <footer>
        <Button
          variant="primary"
          icon={Save}
          submit="lot-form"
          label={t("Sauvegarder")}
        />
        <Button
          asideX
          icon={Return}
          label={t("Retour")}
          action={close}
        />
      </footer>
    </Dialog>
  )
}

export default TransactionDetails
