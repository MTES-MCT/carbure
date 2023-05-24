import { AxiosError } from "axios"
import { findProductionSites } from "carbure/api"
import { Entity, ProductionSite } from "carbure/types"
import { normalizeProductionSite } from "carbure/utils/normalizers"
import AutoComplete from "common/components/autocomplete"
import Button from "common/components/button"
import Collapse from "common/components/collapse"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { AlertOctagon, Check, Return, Upload } from "common/components/icons"
import { FileInput } from "common/components/input"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import useScrollToRef from "common/hooks/scroll-to-ref"
import { DoubleCountingUploadErrors } from "double-counting/types"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { getErrorText } from "settings/utils/double-counting"
import * as api from "../api/double-counting"

type DoubleCountingUploadDialogProps = {
  entity: Entity
  onClose: () => void
}

const DoubleCountingUploadDialog = ({
  entity,
  onClose,
}: DoubleCountingUploadDialogProps) => {
  const { t } = useTranslation()
  const [errors, setErrors] = useState<DoubleCountingUploadErrors>()
  const notify = useNotify()
  const { refToScroll } = useScrollToRef(!!errors)

  const { value, bind } = useForm({
    productionSite: undefined as ProductionSite | undefined,
    doubleCountingFile: undefined as File | undefined,
    documentationFile: undefined as File | undefined,
  })

  const uploadFile = useMutation(api.uploadDoubleCountingFile, {
    onError: (err) => {
      const error = (err as AxiosError<{ error: string }>).response?.data.error
      if (error === "DOUBLE_COUNTING_IMPORT_FAILED") {
        const errors = (
          err as AxiosError<{ data: { errors: DoubleCountingUploadErrors } }>
        ).response?.data?.data?.errors
        setErrors(errors)
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

  const uploadDocFile = useMutation(api.uploadDoubleCountingDescriptionFile)

  const disabled =
    !value.productionSite ||
    !value.doubleCountingFile ||
    !value.documentationFile

  async function submitAgreement() {
    if (
      !entity ||
      !value.productionSite ||
      !value.doubleCountingFile ||
      !value.documentationFile
    )
      return

    try {
      const res = await uploadFile.execute(
        entity.id,
        value.productionSite.id,
        value.doubleCountingFile
      )

      if (res.data.data) {
        await uploadDocFile.execute(
          entity.id,
          res.data.data.dca_id,
          value.documentationFile
        )
        notify(t("Votre dossier double comptage a bien été envoyé !"), {
          variant: "success",
        })
        onClose()
      }
    } catch (error) {}
  }

  return (
    <Dialog onClose={onClose} fullscreen>
      <header>
        <h1>{t("Création dossier double comptage")}</h1>
      </header>

      <main>
        <section>
          <Form id="dc-request">
            <p>
              <Trans>
                Dans un premier temps, renseignez le site de production concerné
                par votre demande.
              </Trans>
            </p>

            <AutoComplete
              autoFocus
              label={t("Site de production")}
              placeholder={t("Rechercher un site de production")}
              getOptions={(search) => findProductionSites(search, entity.id)}
              normalize={normalizeProductionSite}
              {...bind("productionSite")}
            />

            <p>
              <a href="/api/v3/doublecount/get-template">
                <Trans>Téléchargez le modèle depuis ce lien</Trans>
              </a>{" "}
              <Trans>
                puis remplissez les <b>deux premiers onglets</b> afin de
                détailler vos approvisionnements et productions sujets au double
                comptage. Ensuite, importez ce fichier avec le bouton ci-dessous
                :
              </Trans>
            </p>

            <FileInput
              icon={value.doubleCountingFile ? Check : Upload}
              label={t("Importer les informations double comptage")}
              {...bind("doubleCountingFile")}
            />

            <p>
              <Trans>
                Finalement, veuillez importer un fichier texte contenant la
                description de vos méthodes d'approvisionnement et de production
                ayant trait au double comptage.
              </Trans>
            </p>

            <FileInput
              icon={value.documentationFile ? Check : Upload}
              label={t("Importer la description")}
              {...bind("documentationFile")}
            />

            {errors && (
              <section ref={refToScroll}>
                <BlockingErrors errors={errors} />
              </section>
            )}
          </Form>
        </section>
      </main>

      <footer>
        <Button
          asideX
          submit="dc-request"
          loading={uploadFile.loading || uploadDocFile.loading}
          disabled={disabled}
          variant="primary"
          icon={Check}
          action={submitAgreement}
          label={t("Soumettre le dossier")}
        />
        <Button icon={Return} action={onClose} label={t("Annuler")} />
      </footer>
    </Dialog>
  )
}

export default DoubleCountingUploadDialog

export interface BlockingErrorsProps {
  errors: DoubleCountingUploadErrors
}

const BlockingErrors = ({ errors }: BlockingErrorsProps) => {
  const allErrors = [
    ...(errors?.global ?? []),
    // ...(errors?.sourcing_history ?? []),
    ...(errors?.production ?? []),
  ]
  const { t } = useTranslation()
  return (
    <Collapse
      isOpen={true}
      variant="danger"
      icon={AlertOctagon}
      label={`${t("Erreurs")} (${allErrors.length})`}
    >
      <section>
        {t(
          "Vous ne pouvez pas valider ce dossier tant que les problèmes suivants n'ont pas été corrigés. Merci de modifiez le fichier excel et resoumettez-le."
        )}
      </section>

      <footer>
        <ul>
          {errors.global?.map((error, i) => (
            <li key={i}>{getErrorText(error)}</li>
          ))}
          {/* {errors.sourcing_history?.map((error, i) => (
            <li key={i}>
              {t("Approvisionnement") + " - " + getErrorText(error)}
            </li>
          ))} */}
          {errors.production?.map((error, i) => (
            <li key={i}>{t("Production") + " - " + getErrorText(error)}</li>
          ))}
        </ul>
      </footer>
    </Collapse>
  )
}
