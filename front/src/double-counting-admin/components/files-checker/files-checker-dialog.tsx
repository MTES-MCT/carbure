import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { Check, Return, Upload } from "common/components/icons"
import { FileListInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { CheckDoubleCountingFilesResponse } from "double-counting-admin/types"
import { useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import * as api from "../../api"

type DoubleCountingFilesCheckerDialogProps = {
  onClose: () => void
}

const DoubleCountingFilesCheckerDialog = ({
  onClose,
}: DoubleCountingFilesCheckerDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const entity = useEntity()

  const { value, bind } = useForm({
    doubleCountingFiles: undefined as FileList | undefined | null,
  })

  const uploadFiles = useMutation(api.checkDoubleCountingFiles, {
    onError: (err) => {
      const response = (err as AxiosError<{ error: string }>).response
      if (response?.status === 413) {
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
            "L'envoi de votre dossier double comptage a échoué. Merci de contacter l'équipe Carbure"
          ),
          {
            variant: "danger",
          }
        )
      }
    },
  })

  async function submitFiles() {
    if (!value.doubleCountingFiles) return
    const resp = await uploadFiles.execute(
      entity.id,
      value.doubleCountingFiles as FileList
    )
    const checkedFiles = resp.data.data
    if (checkedFiles) {
      onClose()
      navigate("/org/9/double-counting/files-checker", {
        state: {
          checkedFiles,
          files: value.doubleCountingFiles
        }
      })
    }
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Vérification de demandes d'agrément")}</h1>
      </header>

      <main>
        <section>
          <Form id="dc-checker">
            <p>
              {t(
                "Cet outil vous permet de faire remonter les erreurs de fichiers double comptage reçus. "
              )}
            </p>

            <FileListInput
              icon={value.doubleCountingFiles ? Check : Upload}
              label={t("Importer les fichiers excel à analyser")}
              {...bind("doubleCountingFiles")}
            />
          </Form>
        </section>
      </main>

      <footer>
        <Button
          submit="dc-request"
          loading={uploadFiles.loading}
          disabled={!value.doubleCountingFiles}
          variant="primary"
          icon={Check}
          action={submitFiles}
          label={t("Vérifier les demandes")}
        />
        <Button icon={Return} action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

export default DoubleCountingFilesCheckerDialog
