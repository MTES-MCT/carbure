import { AxiosError } from "axios"
import useEntity from "common/hooks/entity"
import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { FileInput } from "common/components/inputs2"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import { checkDoubleCountingApplication } from "double-counting/api"
import ErrorsDetailsDialog from "double-counting/components/application-checker/errors-details-dialog"
import ValidDetailsDialog from "double-counting/components/application-checker/valid-details-dialog"
import { Trans, useTranslation } from "react-i18next"

type DoubleCountingFileCheckerDialogProps = {
  onClose: () => void
}

const DoubleCountingFilesCheckerDialog = ({
  onClose,
}: DoubleCountingFileCheckerDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const portal = usePortal()

  const { value, bind } = useForm({
    doubleCountingFile: undefined as File | undefined,
  })

  const uploadFile = useMutation(checkDoubleCountingApplication, {
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

  async function submitFile() {
    if (!value.doubleCountingFile) return
    const resp = await uploadFile.execute(entity.id, value.doubleCountingFile)
    const checkedFile = resp.data?.file

    if (checkedFile) {
      onClose()
      if (checkedFile.error_count) {
        portal((close) => (
          <ErrorsDetailsDialog fileData={checkedFile} onClose={close} />
        ))
      } else {
        portal((close) => (
          <ValidDetailsDialog
            fileData={checkedFile}
            onClose={close}
            file={value.doubleCountingFile as File}
          />
        ))
      }
    }
  }

  return (
    <Dialog
      onClose={onClose}
      header={
        <Dialog.Title>
          {t("Vérification de dossier de double comptage")}
        </Dialog.Title>
      }
      footer={
        <Button
          nativeButtonProps={{ form: "dc-checker" }}
          loading={uploadFile.loading}
          disabled={!value.doubleCountingFile}
          onClick={submitFile}
          type="submit"
          iconId="ri-check-line"
        >
          {t("Vérifier le fichier")}
        </Button>
      }
    >
      <Form id="dc-checker">
        <p>
          {t(
            "Cet outil vous permet de vérifier le dossier au format Excel avant de l'envoyer à la DGEC."
          )}
        </p>
        <p>
          <Trans>
            Le modèle Excel à remplir est disponible{" "}
            <Button
              linkProps={{
                href: "https://www.ecologie.gouv.fr/sites/default/files/documents/Dossier%20de%20demande%20de%20reconnaissance%20au%20double%20comptage%202024_0.xlsx",
              }}
              customPriority="link"
            >
              sur ce lien
            </Button>
            .
          </Trans>
        </p>
        <div>
          <hr />
          <FileInput
            loading={uploadFile.loading}
            label={t("Importer le dossier double comptage à analyser")}
            placeholder={
              value.doubleCountingFile
                ? value.doubleCountingFile.name
                : t("Choisir un fichier")
            }
            {...bind("doubleCountingFile")}
          />
        </div>
      </Form>
    </Dialog>
  )
}

export default DoubleCountingFilesCheckerDialog
