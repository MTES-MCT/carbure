import {
  DoubleCountingUploadError,
  DoubleCountingUploadErrorType,
} from "../../double-counting/types"
import { t } from "i18next"

export function getErrorText(error: DoubleCountingUploadError) {
  let errorText =
    (error.line_number ?? -1) >= 0
      ? t("Ligne {{lineNumber}} : ", { lineNumber: error.line_number })
      : ""

  switch (error.error) {
    case DoubleCountingUploadErrorType.UnkownFeedstock:
      errorText += t(
        "La matière première {{feedstock}} n'est pas reconnue. Vérifiez la syntaxe de ce code.",
        { feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }) }
      )
      break
    case DoubleCountingUploadErrorType.UnkownBiofuel:
      errorText += t(
        "Le biocarburant {{biofuel}} n'est pas reconnu. Vérifiez la syntaxe de ce code.",
        { biofuel: t(error.meta?.biofuel, { ns: "biofuels" }) }
      )
      break
    case DoubleCountingUploadErrorType.MissingBiofuel:
      errorText += t("Le biocarburant est manquant.")
      break
    case DoubleCountingUploadErrorType.MissingFeedstock:
      errorText += t("La matière première est manquante.")
      break
    case DoubleCountingUploadErrorType.MissingEstimatedProduction:
      errorText += t("La production estimée est manquante.")
      break
    case DoubleCountingUploadErrorType.NotDcFeedstock:
      errorText += t(
        "La matière première {{feedstock}} n’est pas comprise dans la liste des matières premières pouvant être double comptées.",
        { feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }) }
      )
      break
    case DoubleCountingUploadErrorType.MpBcIncoherent:
      errorText += t(
        "La matière première {{feedstock}} est incohérente avec le biocarburant {{biofuel}}.",
        {
          feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }),
          biofuel: t(error.meta?.biofuel, { ns: "biofuels" }),
        }
      )
      if (error.meta?.infos) {
        errorText += " " + error.meta.infos.join(" ")
      }
      break
    case DoubleCountingUploadErrorType.ProductionMismatchSourcing:
      errorText += t(
        "En {{year}}, la quantité de matière première approvisionnée ({{sourcing}} tonnes de {{feedstock}}) doit être supérieure à la quantité de biocarburant produite estimée ({{production}} tonnes).",
        {
          year: error.meta?.year,
          feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }),
          production: error.meta?.production,
          sourcing: error.meta?.sourcing,
        }
      )
      break
    case DoubleCountingUploadErrorType.PomeGt2000:
      errorText += t(
        "La production estimée de biocarburant à partir de EFFLUENTS_HUILERIES_PALME_RAFLE ne doit pas excéder 2000 tonnes par an pour une usine de production."
      )
      break

    default:
      errorText += t("Erreur de validation") + ` (${error.error})`
      break
  }

  return errorText
}
