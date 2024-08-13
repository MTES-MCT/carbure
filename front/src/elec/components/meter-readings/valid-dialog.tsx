import useEntity from "carbure/hooks/entity"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { Return, Send } from "common/components/icons"
import { useNotify, useNotifyError } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import Tag from "common/components/tag"
import { useMutation } from "common/hooks/async"
import * as api from "elec/api-cpo"
import { ElecMeterReadingsApplicationCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"

export type MeterReadingsValidDetailsDialogProps = {
  fileData: ElecMeterReadingsApplicationCheckInfo
  onClose: () => void
  file: File
}

export const MeterReadingsValidDetailsDialog = ({
  fileData,
  onClose,
  file,
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
      notify(
        t("Les {{count}} relevés trimestriels ont bien été envoyés !", {
          count: fileData.charge_point_count,
        }),
        { variant: "success" }
      )
    },
    onError(err) {
      notifyError(err, t("Impossible d'envoyer les relevés trimestriels."))
    },
  })

  const submitMeterReadingsApplication = () => {
    meterReadingsApplication.execute(entity.id, file)
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <Tag big variant="success">
          {t("Valide")}
        </Tag>
        <h1>
          {t("Relevés trimestriels - T{{quarter}} {{year}}", {
            quarter: fileData.quarter,
            year: fileData.year,
          })}
        </h1>
      </header>

      <main>
        <section>
          <p style={{ textAlign: "left" }}>
            <Trans
              values={{
                fileName: fileData.file_name,
              }}
              defaults="Votre fichier <b>{{fileName}}</b> ne comporte aucune erreur."
            />
          </p>
          <p>
            <Trans
              count={fileData.charge_point_count}
              values={{
                quarter: fileData.quarter,
                year: fileData.year,
              }}
              defaults="Votre relevé trimestriel T{{quarter}} {{year}} pour vos {{count}} points de recharge peut être transmis à la DGEC pour vérification."
            />
          </p>
        </section>
      </main>

      <footer>
        <Button
          icon={Send}
          loading={meterReadingsApplication.loading}
          label={t("Transmettre mes relevés trimestriels")}
          variant="primary"
          action={submitMeterReadingsApplication}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>
    </Dialog>
  )
}

export default MeterReadingsValidDetailsDialog
