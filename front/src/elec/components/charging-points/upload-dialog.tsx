import { AxiosError } from "axios"
import useEntity from "carbure/hooks/entity"
import Button, { ExternalLink } from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { AlertCircle, Check, Return, Upload } from "common/components/icons"
import { FileInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"

import { ElecChargingPointsApplicationCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { checkChargingPointsApplication } from "elec/api-cpo"
import ErrorsDetailsDialog from "./errors-dialog"
import ValidDetailsDialog from "./valid-dialog"
import Alert from "common/components/alert"
import { ReplaceAlert } from "./replace-alert"

type ElecChargingPointsFileUploadProps = {
  onClose: () => void
  pendingApplicationAlreadyExists: boolean
}

const ElecChargingPointsFileUpload = ({
  onClose,
  pendingApplicationAlreadyExists,
}: ElecChargingPointsFileUploadProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const portal = usePortal()

  const { value, bind } = useForm({
    chargingPointsFile: undefined as File | undefined,
  })

  const checkChargingPointsFile = useMutation(checkChargingPointsApplication, {
    onSuccess: (res) => {
      const checkedData = res.data.data
      portal((close) => <ValidDetailsDialog fileData={checkedData!} onClose={close} file={value.chargingPointsFile!} />)
      onClose()
    },
    onError: (err) => {

      const response = (err as AxiosError<{ status: string, error: string, data: ElecChargingPointsApplicationCheckInfo }>).response
      if (response?.status === 400) {
        const checkedData = response.data.data
        portal((close) => <ErrorsDetailsDialog fileData={checkedData} onClose={close} />)


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
    checkChargingPointsFile.execute(
      entity.id,
      value.chargingPointsFile as File
    )
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
              loading={checkChargingPointsFile.loading}
              icon={value.chargingPointsFile ? Check : Upload}
              label={t("Importer le fichier excel à analyser")}
              placeholder={value.chargingPointsFile ? value.chargingPointsFile.name : t("Choisir un fichier")}
              {...bind("chargingPointsFile")}
            />
          </Form>
          {pendingApplicationAlreadyExists &&
            (
              <ReplaceAlert />
            )}

        </section>
      </main>

      <footer>
        <Button
          submit="dc-request"
          loading={checkChargingPointsFile.loading}
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
