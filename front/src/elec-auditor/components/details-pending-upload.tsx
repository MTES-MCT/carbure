import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import { UploadCheckReportInfo } from "carbure/types"
import Button from "common/components/button"
import Form, { useForm } from "common/components/form"
import { Check, Send, Upload } from "common/components/icons"
import { FileInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import * as api from "elec-auditor/api"
import { ElecAuditorApplicationDetails } from "elec-auditor/types"
import { useTranslation } from "react-i18next"



const UploadReportSection = ({ application, header, onReportUploaded }: {
  application: ElecAuditorApplicationDetails,
  header: JSX.Element,
  onReportUploaded: () => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()

  const { value, bind } = useForm({
    file: undefined as File | undefined,
  })


  const checkAuditReport = useMutation(api.checkAuditReport, {
    onSuccess: (res) => {
      const checkedData = res.data.data
      console.log('checkedData:', checkedData)

      onReportUploaded()

    },
    onError: (err) => {
      const response = (err as AxiosError<{ status: string, error: string, data: UploadCheckReportInfo }>).response

      if (response?.status === 400 && response.data.error === "VALIDATION_FAILED") {
        const checkedData = response!.data.data
        console.log('checkedData:', checkedData)
      } else if (response?.status === 413) {
        notify(
          t(
            "La taille des fichiers selectionnés est trop importante pour être analysée (5mo maximum)."
          ),
          {
            variant: "danger",
          }
        )
      } else {
        notify(
          t(
            "L'envoi de vos relevés trimestriel a échoué. Merci de contacter l'équipe Carbure"
          ),
          {
            variant: "danger",
          }
        )
      }
    }
  })


  const uploadFile = () => {
    if (!application?.sample) return
    checkAuditReport.execute(entity.id, application.sample.application_id, value.file!)
  }

  return <>
    <main>
      {header}
      <section>
        <Form id="audit-checker">

          <p>{t("Cet outil vous permet de vérifier votre résultat d'audit avant de l'envoyer à la DGEC.")}</p>

          <FileInput
            loading={checkAuditReport.loading}
            icon={value.file ? Check : Upload}
            label={t("Importer le fichier excel à analyser")}
            placeholder={value.file ? value.file.name : t("Choisir un fichier")}
            {...bind("file")}
          />

        </Form>
      </section>
    </main>
    <footer>
      <Button icon={Send} label={t("Vérifier le fichier")} variant="primary" action={uploadFile} disabled={!value.file} />
    </footer>
  </>
}


export default UploadReportSection