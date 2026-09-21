import { ReactNode } from "react"
import { Trans, useTranslation } from "react-i18next"
import { useLocation, useNavigate } from "react-router-dom"

import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Form } from "common/components/form2"
import { FileInput } from "common/components/inputs2"
import Portal from "common/components/portal"
import { Text } from "common/components/text"
import { ExcelImportErrors } from "common/molecules/excel-import-errors"
import useEntity from "common/hooks/entity"

import { downloadActionImportTemplate } from "traceability/api"
import { ActionIndustry } from "traceability/types"
import { useActionExcelImportDialog } from "./action-excel-import-dialog.hooks"

export type ActionExcelImportDialogProps = {
  description: ReactNode
  industry: ActionIndustry
  fieldLabels?: Record<string, string>
}

export const ActionExcelImportDialog = ({
  description,
  industry,
  fieldLabels,
}: ActionExcelImportDialogProps) => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const entity = useEntity()

  const closeDialog = () => {
    navigate({ search: location.search, hash: "#" })
  }

  const { form, loading, importErrors, handleFileChange, handleSubmit } =
    useActionExcelImportDialog({ industry, onClose: closeDialog })

  return (
    <Portal onClose={closeDialog}>
      <Dialog
        onClose={closeDialog}
        header={<Dialog.Title>{t("Import Excel")}</Dialog.Title>}
        footer={
          <Button
            type="submit"
            nativeButtonProps={{ form: "action-excel-import-form" }}
            loading={loading}
            disabled={!form.value.file}
          >
            {t("Importer")}
          </Button>
        }
        size="large"
      >
        <Text>{description}</Text>
        <Text margin>
          <Trans>
            Avant de commencer, veillez à télécharger le modèle disponible{" "}
            <Button
              customPriority="link"
              onClick={() => downloadActionImportTemplate(entity.id, industry)}
            >
              sur ce lien
            </Button>
            .
          </Trans>
        </Text>
        <Form id="action-excel-import-form" form={form} onSubmit={handleSubmit}>
          <FileInput
            label={t("Fichier Excel")}
            placeholder={
              form.value.file
                ? form.value.file.name
                : t("Choisir un fichier (*.xlsx)")
            }
            value={form.value.file}
            onChange={handleFileChange}
            accept=".xlsx,.xls"
            required
          />
          {importErrors && importErrors.validation_errors.length > 0 && (
            <ExcelImportErrors
              importErrors={importErrors}
              fieldLabels={fieldLabels}
            />
          )}
        </Form>
      </Dialog>
    </Portal>
  )
}
