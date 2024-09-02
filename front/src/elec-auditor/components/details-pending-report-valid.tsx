import { UploadCheckReportInfo } from "carbure/types"
import Button from "common/components/button"
import { ChevronLeft, Message, Send } from "common/components/icons"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { Trans, useTranslation } from "react-i18next"
import * as api from "elec-auditor/api"
import useEntity from "carbure/hooks/entity"
import Alert from "common/components/alert"

const ReportValidSection = ({ applicationId, header, file, fileName, onReportAccepted, commentCount, onPrev }: {
  applicationId: number,
  header: JSX.Element,
  file: File,
  fileName: string,
  commentCount?: number,
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
      <section>

        <p><Trans defaults={"Votre fichier d'audit <b>{{ fileName }}</b> ne comporte aucune erreur. Les informations peuvent être transmises à la DGEC."} values={{ fileName }} /></p>
        {!!commentCount &&
          <Alert icon={Message} variant="info" >
            <Trans defaults={"Vous avez commentés <b>{{ count }} points de charges </b> dans ce fichier excel. Ils seront transmis à l'administration."} values={{ count: commentCount }} />
          </Alert>
        }
      </section>
    </main >
    <footer>
      <Button icon={Send} label={t("Transmettre le résultat d'audit")} variant="primary" action={onAcceptFile} loading={acceptAuditReport.loading} />
      <Button icon={ChevronLeft} label={t("Précédent")} variant="secondary" action={onPrev} asideX />

    </footer>
  </>
}


export default ReportValidSection