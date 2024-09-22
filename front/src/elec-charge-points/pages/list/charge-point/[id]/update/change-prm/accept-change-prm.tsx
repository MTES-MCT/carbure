import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Check, Return } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { PortalInstance } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "../api"
import { ChangeMeasureReferencePointQuery } from "../types"

type AcceptChangeMeasureReferencePointProps = {
  onClose: PortalInstance["close"]
  data: ChangeMeasureReferencePointQuery
  onMeasureReferencePointChanged: () => void
}

export const AcceptChangeMeasureReferencePoint = ({
  onClose,
  data,
  onMeasureReferencePointChanged,
}: AcceptChangeMeasureReferencePointProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const mutation = useMutation(api.changeMeasureReferencePoint, {
    invalidates: ["charge-points-details"],
    onSuccess: () => {
      notify(t("Le changement de PRM a bien été pris en compte."), {
        variant: "success",
      })
      onClose()
      onMeasureReferencePointChanged()
    },
    onError: () => {
      notify(t("Une erreur est survenue lors du changement de PRM."), {
        variant: "danger",
      })
    },
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Déclarer un changement de PRM")}</h1>
      </header>
      <main>
        <section>
          <p>
            {t(
              "Souhaitez-vous confirmer le remplacement du PRM pour ce point de recharge ?"
            )}
            <br />
            <br />
            {t(
              "L’ancien PRM sera sauvegardé dans notre base de données, mais ne sera plus visible dans votre espace CarbuRe."
            )}
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
