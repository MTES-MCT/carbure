import { useTranslation } from "react-i18next"
import { ImportErrorResponse } from "./supply-excel-import-dialog"
import { Notice } from "common/components/notice"
import { Text } from "common/components/text"

export const ExcelImportErrors = ({
  importErrors,
}: {
  importErrors: ImportErrorResponse
}) => {
  const { t } = useTranslation()
  const fieldLabels = {
    feedstock: t("Intrant"),
    type_cive: t("Type de CIVE"),
    culture_details: t("Précisez la culture"),
    collection_type: t("Type de collecte"),
    volume: t("Volume"),
    average_weighted_distance_km: t("Distance moyenne pondérée"),
    maximum_distance_km: t("Distance maximale"),
    origin_country: t("Pays d'origine"),
    origin_department: t("Département d'origine"),
  }
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
                        field:
                          fieldLabels[field as keyof typeof fieldLabels] ??
                          field,
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
