import { useState } from "react"
import { useTranslation } from "react-i18next"

import { useForm } from "common/components/form2"
import { useNotify, useNotifyError } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import useEntity from "common/hooks/entity"
import { ImportErrorResponse } from "common/molecules/excel-import-errors"
import { HttpError } from "common/services/api-fetch"

import { importActionsFromExcel } from "traceability/api"
import { ActionIndustry } from "traceability/types"

type ImportFormData = {
  file: File | undefined
}

type UseActionExcelImportDialogParams = {
  industry: ActionIndustry
  onClose: () => void
}

function isImportErrorResponse(data: unknown): data is ImportErrorResponse {
  return (
    typeof data === "object" &&
    data !== null &&
    Array.isArray((data as ImportErrorResponse).validation_errors)
  )
}

export const useActionExcelImportDialog = ({
  industry,
  onClose,
}: UseActionExcelImportDialogParams) => {
  const entity = useEntity()
  const notify = useNotify()
  const notifyError = useNotifyError()
  const { t } = useTranslation()
  const [importErrors, setImportErrors] = useState<ImportErrorResponse | null>(
    null
  )

  const form = useForm<ImportFormData>({
    file: undefined,
  })

  const { execute, loading } = useMutation(importActionsFromExcel, {
    invalidates: ["traceability-actions", "traceability-actions-years"],
    onSuccess: () => {
      notify(t("Les lots ont bien été importés."), { variant: "success" })
      onClose()
    },
    onError: (error) => {
      const data = error instanceof HttpError ? error.data : undefined
      if (isImportErrorResponse(data)) {
        setImportErrors(data)
        return
      }

      notifyError(
        new Error(
          t(
            "Erreur lors de l'import du fichier. Veuillez vérifier le format et réessayer."
          )
        )
      )
    },
  })

  const handleFileChange = (file: File | undefined) => {
    form.setField("file", file)
    setImportErrors(null)
  }

  const handleSubmit = () => {
    if (!form.value.file) {
      return
    }
    setImportErrors(null)
    execute(entity.id, industry, form.value.file)
  }

  return {
    form,
    loading,
    importErrors,
    handleFileChange,
    handleSubmit,
  }
}
