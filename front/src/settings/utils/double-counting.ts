import { DoubleCountingUploadError, DoubleCountingUploadErrorType } from "doublecount/types"
import { t } from "i18next"

export function getErrorText(error: DoubleCountingUploadError) {
    let errorText = error.line_number
        ? t("Ligne {{lineNumber}} : ", { lineNumber: error.line_number })
        : ""

    switch (error.error) {
        case DoubleCountingUploadErrorType.UnkownFeedstock:
            errorText += t(
                "La matière première {{feedstock}} n'est pas reconnue. Vérifiez la syntaxe de ce code.",
                { feedstock: error.meta?.feedstock ?? "" }
            )
            break

        default:
            errorText += t("Erreur de validation")
            break
    }
    return errorText
}
