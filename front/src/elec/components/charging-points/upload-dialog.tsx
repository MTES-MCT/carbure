import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import Button, { ExternalLink } from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { Check, Return, Upload } from "common/components/icons"
import { FileInput, FileListInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"

import { Trans, useTranslation } from "react-i18next"
import { useNavigate } from "react-router-dom"
import { checkDoubleCountingApplication } from "settings/api/double-counting"
import { checkChargingPointsApplication } from "settings/api/elec"
import ErrorsDetailsDialog from "./errors-dialog"
import ValidDetailsDialog from "./valid-dialog"
import { elecChargingPointsApplicationCheckResponseFailed, elecChargingPointsApplicationCheckResponseSucceed } from "elec/__test__/data"

// L'URL complète du fichier


type ElecChargingPointsFileUploadProps = {
  onClose: () => void
}

const ElecChargingPointsFileUpload = ({
  onClose,
}: ElecChargingPointsFileUploadProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const navigate = useNavigate()
  const entity = useEntity()
  const portal = usePortal()

  const { value, bind } = useForm({
    chargingPointsFile: undefined as File | undefined,
  })

  const uploadFile = useMutation(checkChargingPointsApplication, {
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
            "L'envoi de votre inscription des points de recharge a échoué. Merci de contacter l'équipe Carbure"
          ),
          {
            variant: "danger",
          }
        )
      }
    },
  })

  async function submitFile() {
    if (!value.chargingPointsFile) return

    const response = await uploadFile.execute(
      entity.id,
      value.chargingPointsFile as File
    )

    if (response.status != 200) return
    const checkedFile = response.data.data
    // const checkedFile = elecChargingPointsApplicationCheckResponseFailed // TEST with error
    // const checkedFile = elecChargingPointsApplicationCheckResponseSucceed // TEST with success



    if (checkedFile) {
      onClose()
      if (checkedFile.error_count) {
        portal((close) => <ErrorsDetailsDialog fileData={checkedFile} onClose={close} />)
      } else {
        portal((close) => <ValidDetailsDialog fileData={checkedFile} onClose={close} file={value.chargingPointsFile!} />)
      }
    }
  }
  const filePath = '/templates/points-de-recharge-inscription.xlsx';
  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Inscription de points de recharge")}</h1>
      </header>

      <main>
        <section>
          <Form id="dc-checker">
            <p>
              {t(
                "Cet outil vous permet de vérifier la conformité de votre demande d’inscription."
              )}
            </p>
            <p>
              <Trans>
                Le modèle Excel à remplir est disponible {" "}
                <ExternalLink href={filePath}>
                  sur ce lien
                </ExternalLink>
                .
              </Trans>
            </p>
            <FileInput
              loading={uploadFile.loading}
              icon={value.chargingPointsFile ? Check : Upload}
              label={t("Importer le fichier excel à analyser")}
              placeholder={value.chargingPointsFile ? value.chargingPointsFile.name : t("Choisir un fichier")}
              {...bind("chargingPointsFile")}
            />
          </Form>
        </section>
      </main>

      <footer>
        <Button
          submit="dc-request"
          loading={uploadFile.loading}
          disabled={!value.chargingPointsFile}
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

export default ElecChargingPointsFileUpload
