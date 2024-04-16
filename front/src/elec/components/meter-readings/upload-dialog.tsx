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

import * as api from "elec/api-cpo"
import { ElecMeterReadingsApplicationCheckInfo, ElecMeterReadingsCurrentApplicationsPeriod, MeterReadingsApplicationUrgencyStatus } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import MeterReadingsErrorsDetailsDialog from "./errors-dialog"
import { ReplaceAlert } from "./replace-alert"
import MeterReadingsValidDetailsDialog from "./valid-dialog"
import Alert from "common/components/alert"
import { formatDate } from "common/utils/formatters"

type ElecMeterReadingsFileUploadProps = {
  onClose: () => void
  companyId: number
  pendingApplicationAlreadyExists: boolean
  currentApplicationPeriod: ElecMeterReadingsCurrentApplicationsPeriod
}

const ElecMeterReadingsFileUpload = ({
  onClose,
  currentApplicationPeriod,
  companyId,
  pendingApplicationAlreadyExists,
}: ElecMeterReadingsFileUploadProps) => {
  const { t } = useTranslation()
  const notify = useNotify()
  const entity = useEntity()
  const portal = usePortal()
  const TEMPLATE_URL = "/api/elec/cpo/meter-readings/application-template"

  const { value, bind } = useForm({
    meterReadingsFile: undefined as File | undefined,
  })

  const checkMeterReadingsFile = useMutation(api.checkMeterReadingsApplication, {
    onSuccess: (res) => {
      const checkedData = res.data.data
      portal((close) => <MeterReadingsValidDetailsDialog fileData={checkedData!} onClose={close} file={value.meterReadingsFile!} />)
      onClose()
    },
    onError: (err) => {

      const response = (err as AxiosError<{ status: string, error: string, data: ElecMeterReadingsApplicationCheckInfo }>).response

      // TO TEST SUCCESS
      // const checkedData = meterReadingsApplicationCheckResponseSuccess
      // portal((close) => <MeterReadingsValidDetailsDialog fileData={checkedData!} onClose={close} file={value.meterReadingsFile!} />)
      // return

      // TO TEST ERROR
      // const checkedData = meterReadingsApplicationCheckResponseFailed
      // portal((close) => <MeterReadingsErrorsDetailsDialog fileData={checkedData} onClose={close} />)
      // return

      if (response?.status === 400 && response.data.error === "VALIDATION_FAILED") {
        const checkedData = response!.data.data
        portal((close) => <MeterReadingsErrorsDetailsDialog fileData={checkedData} onClose={close} />)
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
      value.meterReadingsFile as File,
    )
  }

  return (
    <Dialog onClose={onClose}>
      <header>
        <h1>{t("Relevés trimestriels - T{{quarter}} {{year}}", { quarter: currentApplicationPeriod.quarter, year: currentApplicationPeriod.year })}</h1>
      </header>

      <main>
        <section>
          <Form id="dc-checker">
            {!pendingApplicationAlreadyExists && <>
              {currentApplicationPeriod.urgency_status === MeterReadingsApplicationUrgencyStatus.Low &&
                <Alert icon={AlertCircle} variant="info">
                  <Trans>A transmettre avant le {formatDate(currentApplicationPeriod.deadline)}</Trans>
                </Alert>
              }
              {currentApplicationPeriod.urgency_status === MeterReadingsApplicationUrgencyStatus.High &&
                <Alert icon={AlertCircle} variant="warning">
                  <Trans>A transmettre avant le {formatDate(currentApplicationPeriod.deadline)}</Trans>
                </Alert>
              }
              {currentApplicationPeriod.urgency_status === MeterReadingsApplicationUrgencyStatus.Critical &&
                <Alert icon={AlertCircle} variant="danger">
                  <Trans>Le delais de déclaration a été dépassé, l'administration se reserve le droit de la refuser.</Trans>
                </Alert>
              }
            </>
            }
            <p>
              {t(
                "Veuillez nous communiquer les relevés de vos points de recharge (kWh) chaque trimestre, pour cela :"
              )}
            </p>
            <ol>
              <li><Trans>
                Téléchargez les relevés du dernier trimestre {" "}
                <ExternalLink href={TEMPLATE_URL + `?entity_id=${entity.id}&company_id=${companyId}`}>
                  sur ce lien
                </ExternalLink>
                .
              </Trans></li>
              <li>
                <Trans>Remplissez les colonnes en bleu (C et D) correspondant aux relevés du trimestre actuel</Trans>
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
              <ReplaceAlert />
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
