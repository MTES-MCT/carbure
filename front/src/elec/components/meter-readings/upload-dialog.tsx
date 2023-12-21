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

import Alert from "common/components/alert"
import * as api from "elec/api-cpo"
import { ElecChargingPointsApplicationCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import ErrorsDetailsDialog from "../charging-points/errors-dialog"
import ValidDetailsDialog from "../charging-points/valid-dialog"
import { meterReadingsApplicationCheckResponseFailed } from "elec/__test__/data"
import MeterReadingsErrorsDetailsDialog from "./errors-dialog"

type ElecMeterReadingsFileUploadProps = {
  onClose: () => void
  quarterString: string
  companyId: number
  pendingApplicationAlreadyExists: boolean
}

const ElecMeterReadingsFileUpload = ({
  onClose,
  quarterString,
  companyId,
  pendingApplicationAlreadyExists,
}: ElecMeterReadingsFileUploadProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const portal = usePortal()
  const TEMPLATE_URL = "/elec/cpo/meter-readings/application-template"

  const { value, bind } = useForm({
    meterReadingsFile: undefined as File | undefined,
  })

  const checkMeterReadingsFile = useMutation(api.checkMeterReadingsApplication, {
    onSuccess: (res) => {
      const checkedData = res.data.data
      portal((close) => <ValidDetailsDialog fileData={checkedData!} onClose={close} file={value.meterReadingsFile!} />)
      onClose()
    },
    onError: (err) => {

      const response = (err as AxiosError<{ status: string, error: string, data: ElecChargingPointsApplicationCheckInfo }>).response

      //TO TEST SUCCESS



      //TO TEST ERROR
      // const checkedData = meterReadingsApplicationCheckResponseFailed
      // portal((close) => <MeterReadingsErrorsDetailsDialog fileData={checkedData} onClose={close} quarterString={quarterString} />)
      // return

      if (response?.status === 400) {
        const checkedData = response!.data.data
        portal((close) => <MeterReadingsErrorsDetailsDialog fileData={checkedData} onClose={close} quarterString={quarterString} />)


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
    },
  })

  async function submitFile() {
    if (!value.meterReadingsFile) return
    checkMeterReadingsFile.execute(
      entity.id,
      value.meterReadingsFile as File
    )
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Relevé trimestriel - {{quarter}}", { quarter: quarterString })}</h1>
      </header>

      <main>
        <section>
          <Form id="dc-checker">
            <p>
              {t(
                "Veuillez nous communiquer les relevés de vos points de recharge (kW) chaque trimestre, pour cela :"
              )}
            </p>
            <ol>
              <li><Trans>
                Téléchargez le relevé du dernier trimestre {" "}
                <ExternalLink href={TEMPLATE_URL + `?entity_id=${entity.id}&company_id=${companyId}`}>
                  sur ce lien
                </ExternalLink>
                .
              </Trans></li>
              <li>
                <Trans>Remplissez la colonne correspondante au trimestre actuel</Trans>
              </li>
              <li>
                <Trans>Déposez le fichier ci-dessous</Trans>
              </li>

            </ol>
            <FileInput
              loading={checkMeterReadingsFile.loading}
              icon={value.meterReadingsFile ? Check : Upload}
              label={t("Importer le fichier excel à analyser")}
              placeholder={value.meterReadingsFile ? value.meterReadingsFile.name : t("Choisir un fichier")}
              {...bind("meterReadingsFile")}
            />
          </Form>
          {pendingApplicationAlreadyExists &&
            (
              <Alert icon={AlertCircle} variant="warning">
                <Trans>Vous avez déjà une demande d'inscription en attente. Cette nouvelle demande viendra écraser la précédente.</Trans>
              </Alert>
            )}

        </section>
      </main>

      <footer>
        <Button
          submit="dc-request"
          loading={checkMeterReadingsFile.loading}
          disabled={!value.meterReadingsFile}
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

export default ElecMeterReadingsFileUpload
