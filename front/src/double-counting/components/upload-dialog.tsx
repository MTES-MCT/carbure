import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import Button, { ExternalLink } from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { Check, Return, Upload } from "common/components/icons"
import { FileInput } from "common/components/input"
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
    const resp = await uploadFile.execute(
      entity.id,
      value.doubleCountingFile as File
    )
    const checkedFile = resp.data.data?.file

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
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Vérification de dossier de double comptage")}</h1>
      </header>

      <main>
        <section>
          <Form id="dc-checker">
            <p>
              {t(
                "Cet outil vous permet de vérifier le dossier au format Excel avant de l'envoyer à la DGEC."
              )}
            </p>
            <p>
              <Trans>
                Le modèle Excel à remplir est disponible{" "}
                <ExternalLink
                  href={
                    "https://www.ecologie.gouv.fr/sites/default/files/Dossier%20de%20demande%20de%20reconnaissance%20au%20double%20comptage%202020.xlsx"
                  }
                >
                  sur ce lien
                </ExternalLink>
                .
              </Trans>
            </p>
            <FileInput
              loading={uploadFile.loading}
              icon={value.doubleCountingFile ? Check : Upload}
              label={t("Importer le fichier excel à analyser")}
              placeholder={
                value.doubleCountingFile
                  ? value.doubleCountingFile.name
                  : t("Choisir un fichier")
              }
              {...bind("doubleCountingFile")}
            />
          </Form>
        </section>
      </main>

      <footer>
        <Button
          submit="dc-request"
          loading={uploadFile.loading}
          disabled={!value.doubleCountingFile}
          variant="primary"
          icon={Check}
          action={submitFile}
          label={t("Vérifier le fichier")}
        />
        <Button icon={Return} action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

export default DoubleCountingFilesCheckerDialog
