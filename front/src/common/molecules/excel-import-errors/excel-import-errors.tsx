import { useTranslation } from "react-i18next"
import { Notice } from "common/components/notice"
import { Text } from "common/components/text"

export interface ValidationError {
  row: number
  errors: Record<string, string[]>
}

export interface ImportErrorResponse {
  validation_errors: ValidationError[]
  total_errors: number
  total_rows_processed: number
}

interface ExcelImportErrorsProps {
  importErrors: ImportErrorResponse
  fieldLabels?: Record<string, string>
}

export const ExcelImportErrors = ({
  importErrors,
  fieldLabels = {},
}: ExcelImportErrorsProps) => {
  const { t } = useTranslation()

  return (
    <Notice variant="alert">
      <div>
        <Text margin>
          {t(
            "({{count}}) erreurs ont été détectées dans le fichier Excel source. Veuillez vous assurer que les intitulés des colonnes sont bien les mêmes que dans notre modèle prédéfini. Merci de corriger le fichier et de l'envoyer à nouveau.",
            { count: importErrors.total_errors }
          )}
        </Text>

        <ul>
          {importErrors.validation_errors.map((validationError, index) => (
            <li key={index}>
              {t("Ligne {{line}} :", { line: validationError.row })}
              <ul>
                {Object.entries(validationError.errors).map(
                  ([field, messages]) => (
                    <li key={field}>
                      {t("Champ {{field}} :", {
                        field: fieldLabels[field] ?? field,
                      })}
                      <ul>
                        {messages.map((message, msgIndex) => (
                          <li key={msgIndex}>{message}</li>
                        ))}
                      </ul>
                    </li>
                  )
                )}
              </ul>
            </li>
          ))}
        </ul>
      </div>
    </Notice>
  )
}
