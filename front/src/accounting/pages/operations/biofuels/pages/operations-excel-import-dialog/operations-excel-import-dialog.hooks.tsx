import { importOperationsFromExcel } from "accounting/api/biofuels/operations"
import { OperationExcelImportRequest } from "accounting/types"
import { useMutation } from "common/hooks/async"
import { ImportErrorResponse } from "common/molecules/excel-import-errors"
import { ModeEnum } from "api-schema"
import { useForm } from "common/components/form2"
import useEntity from "common/hooks/entity"
import { useState } from "react"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useTranslation } from "react-i18next"

type UseOperationsExcelImportDialogParams = {
  onClose: () => void
}

export const useOperationsExcelImportDialog = ({
  onClose,
}: UseOperationsExcelImportDialogParams) => {
  const entity = useEntity()
  const [importErrors, setImportErrors] = useState<ImportErrorResponse | null>(
    null
  )
  const notify = useNotify()
  const { t } = useTranslation()
  const notifyError = useNotifyError()

  const entityId = entity.id

  const form = useForm<Partial<OperationExcelImportRequest>>({
    file: undefined,
    mode: ModeEnum.validate,
  })

  const { execute, loading, result } = useMutation(
    (file: File, importMode: ModeEnum) =>
      importOperationsFromExcel(entityId, file, importMode),
    {
      invalidates: ["operations"],
      onSuccess: () => {
        if (form.value.mode === ModeEnum.validate) {
          form.setField("mode", ModeEnum.create)
          return
        }
        notify(t("Les opérations ont été créées avec succès."), {
          variant: "success",
        })
        onClose()
      },
      onError: (error) => {
        try {
          const errorData = JSON.parse(error.message)
          if (errorData.validation_errors) {
            setImportErrors(errorData as ImportErrorResponse)
            form.setField("mode", ModeEnum.validate)
            return
          }
        } catch {
          // Not JSON, fall through
        }

        notifyError(
          new Error(
            t(
              "Erreur lors de l'import du fichier. Veuillez vérifier le format et réessayer."
            )
          )
        )
      },
    }
  )

  return {
    executeImport: execute,
    loading,
    form,
    operations: result?.data?.operations,
    importErrors,
    setImportErrors,
    isValidated: form.value.mode === ModeEnum.create,
  }
}
