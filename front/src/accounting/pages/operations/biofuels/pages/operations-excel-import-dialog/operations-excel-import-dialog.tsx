import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Trans, useTranslation } from "react-i18next"
import { Form } from "common/components/form"
import { FileInput } from "common/components/inputs2"
import { Notice } from "common/components/notice"
import { Box } from "common/components/scaffold"
import { ExcelImportErrors } from "common/molecules/excel-import-errors"
import { Text } from "common/components/text"
import useEntity from "common/hooks/entity"
import { ModeEnum } from "api-schema"
import { useOperationsExcelImportDialog } from "./operations-excel-import-dialog.hooks"

export const OperationsExcelImportDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()

  const fieldLabels = {
    lot_id: t("N° de lot"),
    volume: t("Volume"),
    operation_type: t("Type d'opération"),
    credited_entity: t("Entité créditée"),
  }

  const {
    executeImport,
    loading,
    form,
    operations,
    importErrors,
    setImportErrors,
    isValidated,
  } = useOperationsExcelImportDialog({
    onClose,
  })
  const { value } = form
  const mode = value.mode

  const handleSubmit = () => {
    setImportErrors(null)
    executeImport(value.file!, mode!)
  }

  const handleFileChange = (file: File | undefined) => {
    form.setField("file", file)
    form.setField("mode", ModeEnum.validate)
    setImportErrors(null)
  }

  const templatePath = `/api/tiruert/operations/import/template/?entity_id=${entity.id}`

  return (
    <Dialog
      header={
        <Dialog.Title>
          {t("Importer des opérations depuis un fichier Excel")}
        </Dialog.Title>
      }
      footer={
        <Button
          type="submit"
          nativeButtonProps={{ form: "operations-import-form" }}
          loading={loading}
          disabled={!value.file}
          priority={isValidated ? "primary" : "secondary"}
        >
          {!isValidated ? t("Valider le fichier") : t("Créer les opérations")}
        </Button>
      }
      onClose={onClose}
      size="large"
    >
      <Notice variant="info" icon="fr-icon-info-line">
        {t(
          "Importez un fichier Excel pour valider ou créer des opérations en masse."
        )}
      </Notice>

      <Box>
        <p>
          <Trans>
            <Text fontWeight="bold">{t("1ère étape :")}</Text>
            Vous devez d'abord télécharger le template contenant vos volumes
            disponibles, en cliquant{" "}
            <Button
              linkProps={{ to: templatePath, target: "_blank" }}
              customPriority="link"
            >
              sur ce lien
            </Button>
            .
          </Trans>
        </p>

        <p>
          <Trans>
            <Text fontWeight="bold">{t("2e étape :")}</Text>
            Une fois le fichier complété, vous pouvez l'uploader ci-dessous pour
            le valider.
          </Trans>
        </p>
        <Form id="operations-import-form" onSubmit={handleSubmit}>
          <FileInput
            loading={loading}
            label={t("Sélectionner le fichier Excel")}
            placeholder={
              value.file ? value.file.name : t("Choisir un fichier (*.xlsx)")
            }
            value={value.file || undefined}
            onChange={handleFileChange}
            state="info"
            stateRelatedMessage={t("Format accepté: .xlsx")}
            required
          />

          {importErrors && importErrors.validation_errors.length > 0 && (
            <ExcelImportErrors
              importErrors={importErrors}
              fieldLabels={fieldLabels}
            />
          )}

          {operations && (
            <Notice
              variant="info"
              title={t(
                "Vous êtes sur le point de créer {{count}} opération(s) :",
                {
                  count: operations.length,
                }
              )}
            >
              <div>
                <strong></strong>
                <ul>
                  {operations.map((op, idx) => (
                    <li key={idx}>
                      {[
                        op.type,
                        op.sector,
                        `${op.total_volume} L`,
                        op.biofuel,
                        op.customs_category,
                        op.credited_entity?.name,
                        t("{{count}} lot(s)", { count: op.lot_count }),
                      ]
                        .filter(Boolean)
                        .join(" - ")}
                    </li>
                  ))}
                </ul>
              </div>
            </Notice>
          )}
        </Form>
      </Box>
    </Dialog>
  )
}
