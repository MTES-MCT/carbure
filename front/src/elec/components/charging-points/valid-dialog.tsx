import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Check, Cross, Plus, Return } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import Tag from "common/components/tag"
import { useMutation } from "common/hooks/async"
import { ElecChargingPointsApplicationCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { applyChargingPoints } from "settings/api/elec"

export type ValidDetailsDialogProps = {
  fileData: ElecChargingPointsApplicationCheckInfo
  onClose: () => void
  file: File
}

export const ValidDetailsDialog = ({
  fileData,
  onClose,
  file
}: ValidDetailsDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const portal = usePortal()

  const chargingPointsApplication = useMutation(applyChargingPoints, {
    invalidates: ["charging-points-applications"],
    onSuccess() {
      onClose()
      notify(t("Les {{count}} points de recharge ont été ajoutés !", { count: fileData.charging_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible d'inscrire les points de recharge"))
    },
  })

  const submitChargingPointsApplication = () => {
    const confirmApplication = () => {
      chargingPointsApplication.execute(entity.id, file)
    }
    if (fileData.pending_application_already_exists) {
      portal((resolve) => (
        <ReplaceApplicationConfirmDialog onClose={resolve} onConfirm={confirmApplication} />
      ))
    } else {
      confirmApplication()
    }
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <Tag big variant="success">
          {t("Valide")}
        </Tag>
        <h1>{t("Inscription des points de recharge")}</h1>
      </header>

      <main>

        <section>
          <p style={{ textAlign: 'left' }}>
            <Trans
              values={{
                fileName: fileData.file_name,
              }}
              defaults="Votre fichier <b>{{fileName}}</b> ne comporte aucune erreur." />
          </p>
          <p>
            <Trans
              count={fileData.charging_point_count}
              defaults="Les <b>{{count}} points de recharge</b> peuvent être inscrits à votre espace CarbuRe." />

          </p>
          <p>
            <Trans>Un échantillon de points de recharge vous sera transmis directement par e-mail de notre part dans le but de réaliser un audit.</Trans>
          </p>

          {fileData.pending_application_already_exists &&
            (
              <Alert icon={AlertCircle} variant="warning">
                <Trans>Vous avez déjà une demande d'inscription en attente. Cete nouvelle demande viendra écraser la précédente.</Trans>
              </Alert>
            )}
        </section>
      </main>

      <footer>
        <Button
          icon={Plus}
          loading={chargingPointsApplication.loading}
          label={fileData.pending_application_already_exists ? t("Remplacer la demande d'inscription") : t("Envoyer la demande d'inscription")}
          variant="primary"
          action={submitChargingPointsApplication}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}


export default ValidDetailsDialog

const ReplaceApplicationConfirmDialog = ({ onClose, onConfirm }: {
  onClose: () => void,
  onConfirm: () => void,
}) => {
  const { t } = useTranslation()

  const confirmApplication = () => {
    onConfirm()
    onClose()
  }

  return <Dialog onClose={onClose}>
    <header>

      <h1>{t("Remplacer la demande d’inscription ?")}</h1>
    </header>

    <main>

      <section>
        <p style={{ textAlign: 'left' }}>
          <Trans>Souhaitez-vous confirmer le remplacement de la précédente demande d’inscription par celle-ci ?</Trans>
        </p>

      </section>
    </main>

    <footer>
      <Button
        icon={Check}
        label={t("Confirmer le remplacement")}
        variant="warning"
        action={confirmApplication}
      />

      <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
    </footer>

  </Dialog>
}
