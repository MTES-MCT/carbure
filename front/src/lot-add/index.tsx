import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { useNotify } from "common-v2/components/notifications"
import { useMutation } from "common-v2/hooks/async"
import Dialog from "common-v2/components/dialog"
import Tag from "common-v2/components/tag"
import Button from "common-v2/components/button"
import { Plus, Return } from "common-v2/components/icons"
import LotForm from "./components/lot-form"
import * as api from "./api"

export const LotAdd = () => {
  const { t } = useTranslation()
  const notify = useNotify()

  const entity = useEntity()

  const navigate = useNavigate()
  const { search } = useLocation()

  const addLot = useMutation(api.addLot, {
    invalidates: ["lots", "snapshot", "year", "lot-summary"],

    onSuccess: (res) => {
      navigate({ pathname: `../drafts/${res.data.data?.id}`, search })
      notify(t("Le lot a bien été créé"), { variant: "success" })
    },

    onError: (res) => {
      notify(t("La création du lot a échoué"), { variant: "danger" })
    },
  })

  const close = () => navigate({ pathname: `../drafts`, search })

  return (
    <Dialog onClose={close}>
      <header>
        <Tag big label={t("Brouillon")} />
        <h1>{t("Créer un nouveau lot")}</h1>
      </header>

      <main>
        <section>
          <LotForm onSubmit={(lot) => addLot.execute(entity.id, lot!)} />
        </section>
      </main>

      <footer>
        <Button
          loading={addLot.loading}
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
