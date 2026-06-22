import { importOperationsFromExcel } from "accounting/api/biofuels/operations"
import { OperationImportResponse } from "accounting/types"
import { useMutation } from "common/hooks/async"
import { ImportErrorResponse } from "common/molecules/excel-import-errors"
import { ModeEnum } from "api-schema"

type UseOperationsExcelImportDialogParams = {
  entityId: number
  mode: ModeEnum
  onValidationSuccess: (result: OperationImportResponse | null) => void
  onCreateSuccess: () => void
  onValidationError: (error: ImportErrorResponse) => void
  onUnknownError: () => void
}

export const useOperationsExcelImportDialog = ({
  entityId,
  mode,
  onValidationSuccess,
  onCreateSuccess,
  onValidationError,
  onUnknownError,
}: UseOperationsExcelImportDialogParams) => {
  const { execute, loading } = useMutation(
    (file: File, importMode: ModeEnum) =>
      importOperationsFromExcel(entityId, file, importMode),
    {
      invalidates: ["operations"],
      onSuccess: (res) => {
        if (mode === ModeEnum.validate) {
          const result =
            (res?.data as OperationImportResponse | undefined) ?? null
          onValidationSuccess(result)
          return
        }

        onCreateSuccess()
      },
      onError: (error) => {
        try {
          const errorData = JSON.parse(error.message)
          if (errorData.validation_errors) {
            onValidationError(errorData as ImportErrorResponse)
            return
          }
        } catch {
          // Not JSON, fall through
        }

        onUnknownError()
      },
    }
  )

  return {
    executeImport: execute,
    loading,
  }
}
