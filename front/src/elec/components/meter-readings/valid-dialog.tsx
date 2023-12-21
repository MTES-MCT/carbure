import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Check, Plus, Return, Send } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import Tag from "common/components/tag"
import { useMutation } from "common/hooks/async"
import * as api from "elec/api-cpo"
import { ElecMeterReadingsApplicationCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { ReplaceAlert } from "./replace-alert"

export type MeterReadingsValidDetailsDialogProps = {
  fileData: ElecMeterReadingsApplicationCheckInfo
  onClose: () => void
  file: File
}

export const MeterReadingsValidDetailsDialog = ({
  fileData,
  onClose,
  file
}: MeterReadingsValidDetailsDialogProps) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const portal = usePortal()

  const meterReadingsApplication = useMutation(api.addMeterReadings, {
    invalidates: ["meter-readings-applications"],
    onSuccess() {
      onClose()
      notify(t("Les {{count}} points de recharge ont été ajoutés !", { count: fileData.charging_point_count }), { variant: "success" })

    },
    onError(err) {
      notifyError(err, t("Impossible d'inscrire les points de recharge"))
    },
  })

  const submitMeterReadingsApplication = () => {
    const confirmApplication = () => {
      meterReadingsApplication.execute(entity.id, file)
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
        <h1>{t("Relevés trimestriels - T{{quarter}} {{year}}", { quarter: fileData.quarter, year: fileData.year })}</h1>
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
              values={{
                quarter: fileData.quarter,
                year: fileData.year,
              }}
              defaults="Votre relevé trimestriel T{{quarter}} {{year}} pour vos {{count}} points de recharge peut-être transmis à la DGEC pour vérification.  peuvent être inscrits à votre espace CarbuRe." />

          </p>


          {fileData.pending_application_already_exists &&
            (
              <ReplaceAlert />
            )}
        </section>
      </main>

      <footer>
        <Button
          icon={Send}
          loading={meterReadingsApplication.loading}
          label={fileData.pending_application_already_exists ? t("Remplacer mes relevés trimestriels") : t("Transmettre mes relevés trimestriels")}
          variant="primary"
          action={submitMeterReadingsApplication}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}


export default MeterReadingsValidDetailsDialog

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

      <h1>{t("Remplacer les derniers relevés ?")}</h1>
    </header>

    <main>

      <section>
        <p style={{ textAlign: 'left' }}>
          <Trans>Souhaitez-vous confirmer le remplacement de vos derniers relevés trimestriels en attente validation par cette nouvelle demande ?</Trans>
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

