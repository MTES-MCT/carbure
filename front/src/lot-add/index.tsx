import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import Dialog from "common-v2/components/dialog"
import Tag from "common-v2/components/tag"
import Button from "common-v2/components/button"
import { Plus, Return } from "common-v2/components/icons"
import LotForm from "./components/lot-form"

export const LotAdd = () => {
  const { t } = useTranslation()

  const navigate = useNavigate()
  const location = useLocation()

  const close = () =>
    navigate({
      pathname: `../drafts`,
      search: location.search,
    })

  return (
    <Dialog onClose={close}>
      <header>
        <Tag big label={t("Brouillon")} />
        <h1>{t("Créer un nouveau lot")}</h1>
      </header>

      <main>
        <section>
          <LotForm onSubmit={(form) => console.log(form)} />
        </section>
      </main>

      <footer>
        <Button
          variant="primary"
          icon={Plus}
          submit="lot-form"
          label={t("Créer lot")}
        />
        <Button asideX icon={Return} label={t("Retour")} action={close} />
      </footer>
    </Dialog>
  )
}

export default LotAdd
