import { UploadCheckReportInfo } from "carbure/types"
import Button from "common/components/button"
import { ChevronLeft, Send } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { useTranslation } from "react-i18next"
import * as api from "elec-auditor/api"
import useEntity from "carbure/hooks/entity"

const ReportValidSection = ({ applicationId, header, file, fileName, onReportAccepted, onPrev }: {
  applicationId: number,
  header: JSX.Element,
  file: File,
  fileName: string,
  onReportAccepted: () => void
  onPrev: () => void
}) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()

  const acceptAuditReport = useMutation(api.acceptAuditReport, {
    invalidates: ["elec-audit-applications", "elec-audit-snapshot"],
    onSuccess: () => {
      onReportAccepted()
      notify(
        t(
          "Le rapport d'audit a été transmis à la DGEC. L'audit est à présent terminé."
        ),
        {
          variant: "success",
        }
      )
    },
    onError: () => {
      notify(
        t(
          "L'envoi de votre rapport d'audit a échoué. Merci de contacter l'équipe Carbure"
        ),
        {
          variant: "danger",
        }
      )
    }
  })

  const onAcceptFile = () => {
    acceptAuditReport.execute(entity.id, applicationId, file)
  }



  return <>
    <main>
      {header}
      <p>{t("Votre fichier d'audit {{fileName}} ne comporte aucune erreur.", { fileName })}</p>
      <p>{t("Les informations peuvent être transmises à la DGEC.")}</p>
    </main>
    <footer>
      <Button icon={Send} label={t("Transmettre le résultat d'audit")} variant="primary" action={onAcceptFile} loading={acceptAuditReport.loading} />
      <Button icon={ChevronLeft} label={t("Précédent")} variant="secondary" action={onPrev} asideX />

    </footer>
  </>
}


export default ReportValidSection