import { Button } from "common/components/button2"
import { Dialog } from "common/components/dialog2"
import { Trans, useTranslation } from "react-i18next"
import { Form, useForm } from "common/components/form"
import { FileInput } from "common/components/inputs2"
import { useMutation } from "common/hooks/async"
import { useNotify, useNotifyError } from "common/components/notifications"
import useEntity from "common/hooks/entity"
import { useState } from "react"
import { importSupplyPlan } from "../api"
import { Notice } from "common/components/notice"
import { Box } from "common/components/scaffold"
import { ExcelImportErrors } from "./excel-import-errors"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

interface ImportFormData {
  supplyPlanFile: File | null
}

interface ValidationError {
  row: number
  errors: Record<string, string[]>
}

export interface ImportErrorResponse {
  validation_errors: ValidationError[]
  total_errors: number
  total_rows_processed: number
}

export const ExcelImportDialog = ({ onClose }: { onClose: () => void }) => {
  const { t } = useTranslation()
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { currentAnnualDeclarationKey } = useAnnualDeclaration()
  const [importErrors, setImportErrors] = useState<ImportErrorResponse | null>(
    null
  )

  const { value, bind } = useForm<ImportFormData>({
    supplyPlanFile: null,
  })

  const { execute: executeImport, loading } = useMutation(importSupplyPlan, {
    invalidates: ["supply-plan-inputs", currentAnnualDeclarationKey],
    onSuccess: () => {
      notify(t("Fichier importé avec succès"), { variant: "success" })
      onClose()
    },
    onError: (error) => {
      const errorData = JSON.parse(error.message)
      if (errorData.validation_errors) {
        setImportErrors(errorData as ImportErrorResponse)
        return
      }

      notifyError(new Error(t("Erreur lors de l'import du fichier")))
    },
  })

  const handleSubmit = () => {
    if (!value.supplyPlanFile) {
      notifyError(new Error(t("Veuillez sélectionner un fichier")))
      return
    }

    setImportErrors(null)
    executeImport(entity.id, value.supplyPlanFile)
  }

  const handleFileChange = (file: File | undefined) => {
    bind("supplyPlanFile").onChange(file || null)
  }

  const filePath = "/api/biomethane/supply-plan/download-template/"

  return (
    <Dialog
      header={
        <Dialog.Title>{t("Importer un plan d'approvisionnement")}</Dialog.Title>
      }
      footer={
        <Button
          type="submit"
          nativeButtonProps={{ form: "supply-plan-import-form" }}
          loading={loading}
          disabled={!value.supplyPlanFile}
        >
          {t("Importer")}
        </Button>
      }
      onClose={onClose}
      size="medium"
    >
      <Notice variant="info" icon="fr-icon-info-line">
        {t(
          "Vous pouvez déposer ici un plan d'approvisionnement afin de le visualiser dans notre outil."
        )}
      </Notice>

      <Box>
        <p>
          <Trans>
            Le template du fichier attendu est disponible{" "}
            <Button
              linkProps={{ to: filePath, target: "_blank" }}
              customPriority="link"
            >
              sur ce lien
            </Button>
            .
          </Trans>
        </p>

        <Form id="supply-plan-import-form" onSubmit={handleSubmit}>
          <FileInput
            loading={loading}
            label={t("Importer le fichier excel")}
            placeholder={
              value.supplyPlanFile
                ? value.supplyPlanFile.name
                : t("Choisir un fichier")
            }
            value={value.supplyPlanFile || undefined}
            onChange={handleFileChange}
            state="info"
            stateRelatedMessage={t(
              "Les intrants déjà importés seront écrasés."
            )}
          />

          {importErrors && importErrors.validation_errors.length > 0 && (
            <ExcelImportErrors importErrors={importErrors} />
          )}
        </Form>
      </Box>
    </Dialog>
  )
}
