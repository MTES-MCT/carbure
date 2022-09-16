import { findProductionSites } from "carbure/api"
import { Entity, ProductionSite } from "carbure/types"
import { normalizeProductionSite } from "carbure/utils/normalizers"
import AutoComplete from "common/components/autocomplete"
import Button from "common/components/button"
import Dialog from "common/components/dialog"
import { Form, useForm } from "common/components/form"
import { Check, Return, Upload } from "common/components/icons"
import { FileInput } from "common/components/input"
import { useMutation } from "common/hooks/async"
import { Trans, useTranslation } from "react-i18next"
import * as api from "../api/double-counting"
import { AxiosError } from "axios"
import { DoubleCountingUploadErrors } from "doublecount/types"

type DoubleCountingUploadDialogProps = {
  entity: Entity
  onClose: () => void
}

const DoubleCountingUploadDialog = ({
  entity,
  onClose,
}: DoubleCountingUploadDialogProps) => {
  const { t } = useTranslation()

  const { value, bind } = useForm({
    productionSite: undefined as ProductionSite | undefined,
    doubleCountingFile: undefined as File | undefined,
    documentationFile: undefined as File | undefined,
  })

  const uploadFile = useMutation(api.uploadDoubleCountingFile, {
    onSuccess: (res) => {
      console.log("okkk:", res)
    },
    // notify(t("La société a été ajoutée !"), { variant: "success" }),
    onError: (err) => {
      // const error = (err as AxiosError<{ error: string }>).response?.data.error
      const errors = (
        err as AxiosError<{ data: { errors: DoubleCountingUploadErrors } }>
      ).response?.data.data.errors
      console.log(">error:", errors)

      // notify(t("La société n'a pas pu être ajoutée !"), { variant: "danger" }),
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

    const res = await uploadFile.execute(
      entity.id,
      value.productionSite.id,
      value.doubleCountingFile
    )

    if (res.data.status === "success" && res.data.data) {
      await uploadDocFile.execute(
        entity.id,
        res.data.data.dca_id,
        value.documentationFile
      )
    }

    onClose()
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
