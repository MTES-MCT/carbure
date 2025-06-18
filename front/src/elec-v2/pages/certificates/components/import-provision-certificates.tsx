import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form, useForm } from "common/components/form2"
import { FileInput } from "common/components/inputs2"
import { useNotify } from "common/components/notifications"
import { usePortal } from "common/components/portal"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { useTranslation } from "react-i18next"
import { importProvisionCertificates } from "../api"

const TEMPLATE_URL = "/templates/certificats-de-fourniture.csv"

export const ImportProvisionCertificates = () => {
  const { t } = useTranslation()
  const portal = usePortal()

  function showDialog() {
    portal((close) => <ImportProvisionCertificatesDialog onClose={close} />)
  }

  return (
    <Button iconId="fr-icon-draft-fill" asideX onClick={showDialog}>
      {t("Émettre des certificats de fourniture")}
    </Button>
  )
}

type ImportProvisionCertificatesDialogProps = {
  onClose: () => void
}

const ImportProvisionCertificatesDialog = ({
  onClose,
}: ImportProvisionCertificatesDialogProps) => {
  const { t } = useTranslation()
  const notify = useNotify()

  const entity = useEntity()

  const form = useForm({
    file: undefined as File | undefined,
  })

  const importResponse = useMutation(importProvisionCertificates, {
    invalidates: [
      "elec-provision-certificates",
      "elec-certificates-snapshot",
      "years",
    ],
    onSuccess() {
      notify(t("Les certificats ont bien été ajoutés"), { variant: "success" })
      onClose()
    },
    onError() {
      notify(t("Le certificat n'ont pas pu être ajoutés"), {
        variant: "danger",
      })
    },
  })

  function onImport() {
    if (form.value.file) {
      importResponse.execute(entity.id, form.value.file)
    }
  }

  return (
    <Dialog
      onClose={onClose}
      header={<Dialog.Title>{t("Importer les certificats")}</Dialog.Title>}
      footer={
        <>
          <Button priority="secondary" onClick={onClose}>
            {t("Annuler")}
          </Button>
          <Button
            loading={importResponse.loading}
            disabled={!form.value.file}
            iconId="fr-icon-check-line"
            type="submit"
            customPriority="success"
            nativeButtonProps={{ form: "import-elec-provision-form" }}
          >
            {t("Importer")}
          </Button>
        </>
      }
    >
      <p>
        {t(
          "En tant qu'administrateur DGEC, vous pouvez importer ici des quantités d'énergie à céder, classés par trimestre et par aménageurs. "
        )}
      </p>

      <p>
        {t("Téléchargez le template à completer et à importer")}{" "}
        <Button
          linkProps={{
            href: location.origin + TEMPLATE_URL + `?entity_id=${entity.id}`,
          }}
          customPriority="link"
        >
          {t("sur ce lien")}
        </Button>
        .
      </p>

      <Form
        id="import-elec-provision-form"
        onSubmit={onImport}
        style={{ marginTop: "var(--spacing-m)" }}
      >
        <FileInput
          required
          label={t("Choisir un fichier .csv")}
          {...form.bind("file")}
        />
      </Form>
    </Dialog>
  )
}
