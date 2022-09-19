import { findProductionSites } from "carbure/api"
import { Entity, ProductionSite } from "carbure/types"
import { normalizeProductionSite } from "carbure/utils/normalizers"
import AutoComplete from "common/components/autocomplete"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { AlertOctagon, Check, Return, Upload } from "common/components/icons"
import { FileInput } from "common/components/input"
import { useMutation } from "common/hooks/async"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/double-counting"
import { AxiosError } from "axios"
import {
  DoubleCountingUploadError,
  DoubleCountingUploadErrors,
  DoubleCountingUploadErrorType,
} from "doublecount/types"
import Collapse from "common/components/collapse"
import { useState } from "react"
import { t } from "i18next"
import { getErrorText } from "settings/utils/double-counting"
import { useNotify } from "common/components/notifications"

type DoubleCountingUploadDialogProps = {
  entity: Entity
  onClose: () => void
}

const DoubleCountingUploadDialog = ({
  entity,
  onClose,
}: DoubleCountingUploadDialogProps) => {
  const { t } = useTranslation()
  const [errors, setErrors] = useState<DoubleCountingUploadError[]>([])
  const notify = useNotify()

  const { value, bind } = useForm({
    productionSite: undefined as ProductionSite | undefined,
    doubleCountingFile: undefined as File | undefined,
    documentationFile: undefined as File | undefined,
  })

  const uploadFile = useMutation(api.uploadDoubleCountingFile, {
    onSuccess: (res) => {
      console.log("okkk:", res)
      notify(t("Votre dossier double comptage a bien été envoyé !"), {
        variant: "success",
      })
    },
    onError: (err) => {
      const error = (err as AxiosError<{ error: string }>).response?.data.error
      console.log("error:", error)
      if (error === "DOUBLE_COUNTING_IMPORT_FAILED") {
        const respErrors = (
          err as AxiosError<{ data: { errors: DoubleCountingUploadErrors } }>
        ).response?.data.data.errors
        console.log(">error:", respErrors)

        const errors = [
          ...(respErrors?.global ?? []),
          ...(respErrors?.sourcing ?? []),
          ...(respErrors?.production ?? []),
        ]
        console.log("errors:", errors)
        setErrors(errors)
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
        onClose()
      }
    } catch (error) {}
  }

  return (
    <Dialog onClose={onClose}>
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

            {errors.length && <BlockingErrors errors={errors} />}
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
  errors: DoubleCountingUploadError[]
}

const BlockingErrors = ({ errors }: BlockingErrorsProps) => {
  const { t } = useTranslation()
  return (
    <Collapse
      variant="danger"
      icon={AlertOctagon}
      label={`${t("Erreurs")} (${errors.length})`}
    >
      <section>
        {t(
          "Vous ne pouvez pas valider ce lot tant que les problèmes suivants n'ont pas été adressés :"
        )}
      </section>

      <footer>
        <ul>
          {errors.map((error, i) => (
            <li key={i}>{getErrorText(error)}</li>
          ))}
        </ul>
      </footer>
    </Collapse>
  )
}
