import Alert from "common/components/alert"
import { useTranslation } from "react-i18next"
import { ImportErrorResponse } from "./supply-excel-import-dialog"

export const ExcelImportErrors = ({
  importErrors,
}: {
  importErrors: ImportErrorResponse
}) => {
  const { t } = useTranslation()

  return (
    <Alert variant="danger" multiline>
      <p style={{ marginBottom: "var(--spacing-l)" }}>
        {t(
          "({{count}}) erreurs ont été détectées dans le fichier Excel source. Veuillez vous assurer que les intitulés des colonnes sont bien les mêmes que dans notre modèle prédéfini. Merci de corriger le fichier et de l'envoyer à nouveau.",
          { count: importErrors.total_errors }
        )}
      </p>

      <ul>
        {importErrors.validation_errors.map((validationError, index) => (
          <li key={index}>
            {t("Ligne {{line}} :", { line: validationError.row })}
            <ul>
              {Object.entries(validationError.errors).map(
                ([field, messages]) => (
                  <li key={field}>
                    {t("Champ {{field}} :", { field })}
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
    </Alert>
  )
}
