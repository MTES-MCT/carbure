import Alert from "common/components/alert"
import { Button } from "common/components/button"
import { Divider } from "common/components/divider"
import { Download, Message } from "common/components/icons"
import { ElecApplicationSample } from "elec-audit-admin/types"
import { Trans, useTranslation } from "react-i18next"
import SampleSummary from "./details-sample-summary"

const SampleDetailsAuditDoneSection = ({
  sample,
  onDownloadSample,
}: {
  sample: ElecApplicationSample
  onDownloadSample: () => void
}) => {
  const { t } = useTranslation()

  const commentCount = sample?.comment_count
  const auditorName = sample?.auditor_name

  return (
    <>
      <section>
        <SampleSummary sample={sample} />
        <Divider />
        <strong>{t("Résultat d'audit")}</strong>
        <p>
          {t(
            "Télécharger directement le fichier d'audit pour visualiser les informations entrées par l'auditeur."
          )}
        </p>
        <Button
          icon={Download}
          label={t("Télécharger le rapport d'audit")}
          variant="secondary"
          action={onDownloadSample}
        />
      </section>
      {commentCount && commentCount > 0 && (
        <section>
          <Alert icon={Message} variant="info">
            <Trans
              defaults={
                "<b>{{ count }} points de charges </b>  ont été commentés par l'auditeur <b>{{auditorName}}</b> dans le fichier excel."
              }
              values={{ count: commentCount, auditorName }}
            />
          </Alert>
        </section>
      )}
    </>
  )
}

export default SampleDetailsAuditDoneSection
