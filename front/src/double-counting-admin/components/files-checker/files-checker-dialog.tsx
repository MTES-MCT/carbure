import { AxiosError } from "axios"
import useEntity from "common/hooks/entity"
import Button from "common/components/button"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form"
import { Check } from "common/components/icons"
import { FileListInput } from "common/components/inputs2"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
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
    doubleCountingFiles: undefined as FileList | undefined,
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
    const resp = await uploadFiles.execute(entity.id, value.doubleCountingFiles)
    const checkedFiles = resp.data
    if (checkedFiles) {
      onClose()
      navigate("/org/9/double-counting/files-checker", {
        state: {
          checkedFiles,
          files: value.doubleCountingFiles,
        },
      })
    }
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>{t("Vérification de demandes d'agrément")}</Dialog.Title>
      }
      footer={
        <Button
          submit="dc-request"
          loading={uploadFiles.loading}
          disabled={!value.doubleCountingFiles}
          variant="primary"
          icon={Check}
          action={submitFiles}
          label={t("Vérifier les demandes")}
        />
      }
    >
      <Form id="dc-checker">
        <p>
          {t(
            "Cet outil vous permet de faire remonter les erreurs de fichiers double comptage reçus. "
          )}
        </p>

        <FileListInput
          label={t("Importer les fichiers excel à analyser")}
          {...bind("doubleCountingFiles")}
        />
      </Form>
    </Dialog>
  )
}

export default DoubleCountingFilesCheckerDialog
