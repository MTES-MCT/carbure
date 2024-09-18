import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { PortalInstance } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../api"
import { AddMeterQuery } from "../types"

type AcceptChangeMeterProps = {
  onClose: PortalInstance["close"]
  data: AddMeterQuery
  onMeterChanged: () => void
}

export const AcceptChangeMeter = ({
  onClose,
  data,
  onMeterChanged,
}: AcceptChangeMeterProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const mutation = useMutation(api.addMeter, {
    invalidates: ["charge-points-details"],
    onSuccess: () => {
      notify("Le champ de compteur MID a bien été pris en compte.", {
        variant: "success",
      })
      onClose()
      onMeterChanged()
    },
    onError: () => {
      notify("Une erreur est survenue lors du changement de compteur MID.", {
        variant: "danger",
      })
    },
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Déclarer un changement de compteur")}</h1>
      </header>
      <main>
        <section>
          <p>
            Souhaitez-vous confirmer le remplacement du N° de compteur MID pour
            ce point de recharge ? <br />
            <br /> L’ancien n° MID sera sauvegardé dans notre base de données,
            mais ne sera plus visible dans votre espace CarbuRe.
          </p>
        </section>
      </main>
      <footer>
        <Button icon={Return} action={onClose} label={t("Retour")} />
        <Button
          variant="primary"
          icon={Check}
          label={t("Confirmer")}
          asideX
          action={() => mutation.execute(entity.id, data)}
          loading={mutation.loading}
        />
      </footer>
    </Dialog>
  )
}
