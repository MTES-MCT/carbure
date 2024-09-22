import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Check } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { PortalInstance, useCloseAllPortals } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { ChargePoint } from "elec-charge-points/types"
import { useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"
import * as api from "./api"

type DeleteChargePointDialogProps = {
  id: ChargePoint["id"]
  onClose: PortalInstance["close"]
}
export const DeleteChargePointDialog = ({
  id,
  onClose,
}: DeleteChargePointDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const entity = useEntity()
  const location = useLocation()
  const mutation = useMutation(api.deleteChargePoint, {
    invalidates: ["charge-points-list", "charge-points-snapshot"],
    onSuccess: () => {
      onClose()
      notify(t("Le point de recharge a bien été supprimé."), {
        variant: "success",
      })
      navigate({ search: location.search, hash: "" })
    },
    onError: () => {
      notify(
        t(
          "Une erreur est survenue lors de la suppression du point de recharge."
        ),
        {
          variant: "danger",
        }
      )
    },
  })

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Supprimer un point de recharge")}</h1>
      </header>
      <main>
        <section>
          {t("Veuillez confirmer la suppression du point de recharge.")}
        </section>
      </main>
      <footer>
        <Button
          variant="primary"
          label={t("Confirmer")}
          action={() => mutation.execute(entity.id, id)}
          icon={Check}
          asideX
          loading={mutation.loading}
        />
      </footer>
    </Dialog>
  )
}
