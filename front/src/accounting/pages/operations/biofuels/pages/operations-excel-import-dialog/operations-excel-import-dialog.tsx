import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Trans, useTranslation } from "react-i18next"
import { Form, useForm } from "common/components/form"
import { FileInput } from "common/components/inputs2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useState } from "react"
import { Notice } from "common/components/notice"
import { Box } from "common/components/scaffold"
import {
  ExcelImportErrors,
  ImportErrorResponse,
} from "common/molecules/excel-import-errors"
import { Text } from "common/components/text"
import useEntity from "common/hooks/entity"
import { ModeEnum } from "api-schema"
import {
  OperationExcelImportRequest,
  OperationImportResponse,
} from "accounting/types"
import { useOperationsExcelImportDialog } from "./operations-excel-import-dialog.hooks"

export const OperationsExcelImportDialog = ({
  onClose,
}: {
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const [importErrors, setImportErrors] = useState<ImportErrorResponse | null>(
    null
  )
  const [validationResult, setValidationResult] =
    useState<OperationImportResponse | null>(null)
  const [validated, setValidated] = useState(false)

  const fieldLabels = {
    lot_id: t("N° de lot"),
    volume: t("Volume"),
    operation_type: t("Type d'opération"),
    credited_entity: t("Entité créditée"),
  }

  const { value, bind } = useForm<OperationExcelImportRequest>({
    file: undefined,
    mode: ModeEnum.validate,
  })

  const mode = value.mode

  const { executeImport, loading } = useOperationsExcelImportDialog({
    entityId: entity.id || 0,
    mode,
    onValidationSuccess: (result) => {
      setValidationResult(result)
      setValidated(true)
      bind("mode").onChange(ModeEnum.create)
    },
    onCreateSuccess: () => {
      notify(t("Les opérations ont été créées avec succès."), {
        variant: "success",
      })
      onClose()
    },
    onValidationError: (errorData) => {
      setImportErrors(errorData)
      setValidated(false)
      bind("mode").onChange(ModeEnum.validate)
      setValidationResult(null)
    },
    onUnknownError: () => {
      notifyError(
        new Error(
          t(
            "Erreur lors de l'import du fichier. Veuillez vérifier le format et réessayer."
          )
        )
      )
    },
  })

  const handleSubmit = () => {
    if (!value.file) {
      notifyError(new Error(t("Veuillez sélectionner un fichier")))
      return
    }

    setImportErrors(null)
    executeImport(value.file, mode)
  }

  const handleFileChange = (file: File | undefined) => {
    bind("file").onChange(file)
    setValidated(false)
    bind("mode").onChange(ModeEnum.validate)
    setImportErrors(null)
    setValidationResult(null)
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
          priority={validated ? "primary" : "secondary"}
        >
          {mode === ModeEnum.validate
            ? t("Valider le fichier")
            : t("Créer les opérations")}
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
            Le modèle du fichier attendu est disponible{" "}
            <Button
              linkProps={{ to: templatePath, target: "_blank" }}
              customPriority="link"
            >
              sur ce lien
            </Button>
            .
          </Trans>
        </p>
        <Text fontWeight="bold">
          {t(
            "Pensez à retélécharger le modèle afin d'avoir les dernières modifications du fichier."
          )}
        </Text>

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
          />

          {importErrors && importErrors.validation_errors.length > 0 && (
            <ExcelImportErrors
              importErrors={importErrors}
              fieldLabels={fieldLabels}
            />
          )}

          {validationResult && (
            <Notice
              variant="info"
              title={t(
                "Vous êtes sur le point de créer {{count}} opération(s) :",
                {
                  count: validationResult.operations.length,
                }
              )}
            >
              <div>
                <strong></strong>
                <ul>
                  {validationResult.operations.map((op, idx) => (
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
