import { useNavigate, useLocation } from "react-router-dom"
import { useTranslation } from "react-i18next"
import useEntity from "carbure/hooks/entity"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import Dialog from "common/components/dialog"
import Tag from "common/components/tag"
import Button from "common/components/button"
import { Plus, Return } from "common/components/icons"
import LotForm, { useLotForm } from "./components/lot-form"
import * as api from "./api"
import { useMatomo } from "matomo"

export const LotAdd = () => {
  const { t } = useTranslation()
  const notify = useNotify()
  const matomo = useMatomo()
  const navigate = useNavigate()
  const { search } = useLocation()

  const entity = useEntity()
  const form = useLotForm()

  const addLot = useMutation(api.addLot, {
    invalidates: ["lots", "snapshot", "years", "lot-summary"],

    onSuccess: (res) => {
      navigate({ pathname: `../drafts/imported/${res.data.data?.id}`, search })
      notify(t("Le lot a bien été créé"), { variant: "success" })
    },

    onError: () => {
      notify(t("La création du lot a échoué"), { variant: "danger" })
    },
  })

  const close = () => navigate({ pathname: `../drafts/imported`, search })

  return (
    <Dialog onClose={close}>
      <header>
        <Tag big label={t("Brouillon")} />
        <h1>{t("Créer un nouveau lot")}</h1>
      </header>

      <main>
        <section>
          <LotForm
            form={form}
            onSubmit={(lot) => {
              matomo.push(["trackEvent", "lots-create", "create-lot-with-form"])
              addLot.execute(entity.id, lot!)
            }}
          />
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
