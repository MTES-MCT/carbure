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
        { feedstock: error.meta?.feedstock }
      )
      break
    case DoubleCountingUploadErrorType.UnkownBiofuel:
      errorText += t(
        "Le biocarburant {{biofuel}} n'est pas reconnu. Vérifiez la syntaxe de ce code.",
        { biofuel: error.meta?.biofuel }
      )
      break
    case DoubleCountingUploadErrorType.MissingBiofuel:
      errorText += t(
        "Le biocarburant est manquant."
      )
      break
    case DoubleCountingUploadErrorType.NotDcFeedstock:
      errorText += t(
        "La matière première {{feedstock}} n’est pas comprise dans la liste des matières premières pouvant être double comptées.",
        { feedstock: error.meta?.feedstock }
      )
      break
    case DoubleCountingUploadErrorType.MpBcIncoherent:
      errorText += t(
        "La matière première {{feedstock}} est incohérente avec le biocarburant {{biofuel}}.",
        { feedstock: error.meta?.feedstock, biofuel: error.meta?.biofuel }
      )
      break
    case DoubleCountingUploadErrorType.ProductionMismatchSupply:
      errorText += t(
        "Le poids de matière première approvisionnée {{feedstock}} ne doit pas être supérieur à la quantité de biocarburant produite estimée.",
        { feedstock: error.meta?.feedstock }
      )
      break
    // case DoubleCountingUploadErrorType.ProductionMismatchSupply:
    //   errorText += t(
    //     "La production éstimée de biocarburant à partir de {{feedstock}} ne doit pas excéder 2000 tonnes par an pour une usine de production",
    //     { feedstock: error.meta?.feedstock  }
    //   )
    //   break

    default:
      errorText += t("Erreur de validation")
      break
  }
  return errorText
}
