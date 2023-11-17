import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Plus, Return } from "common/components/icons"
import { usePortal } from "common/components/portal"
import Tag from "common/components/tag"
import { Trans, useTranslation } from "react-i18next"
import { useMatch } from "react-router-dom"
import FileApplicationInfo from "../../../double-counting/components/files-checker/file-application-info"
import { DoubleCountingFileInfo } from "../../../double-counting/types"
import { ElecChargingPointsApplicationCheckInfo } from "elec/types"
import { subscribeChargingPointsApplication } from "settings/api/elec"
import { useMutation } from "common/hooks/async"
import useEntity from "carbure/hooks/entity"
import { useNotify, useNotifyError } from "common/components/notifications"

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

  const subscribeChargingPoints = useMutation(subscribeChargingPointsApplication, {
    invalidates: ["dc-applications", "dc-snapshot"],
    onSuccess() {
      onClose()
      notify(t("Les {{count}} points de recharge ont été ajoutés !", { count: fileData.charging_points_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible d'inscrire les points de recharge"))
    },
  })

  const submitChargingPointsSubscription = () => {
    subscribeChargingPoints.execute(entity.id, file)
  }

  return (
    <Dialog fullscreen onClose={onClose}>
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
              count={fileData.charging_points_count}
              defaults="Les <b>{{count}} points de recharge</b> peuvent être inscrits à votre espace CarbuRe." />

          </p>
          <p>
            <Trans>Un échantillon de points de recharge vous sera transmis directement par e-mail de notre part dans le but de réaliser un audit.</Trans>
          </p>
        </section>
      </main>

      <footer>
        <Button
          icon={Plus}
          loading={subscribeChargingPoints.loading}
          label={t("Envoyer la demande d'inscription")}
          variant="primary"
          action={submitChargingPointsSubscription}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}




export default ValidDetailsDialog


