import {
  DoubleCountingUploadError,
  DoubleCountingUploadErrorType,
} from "double-counting/types"
import { t } from "i18next"

export function getErrorText(
  error: DoubleCountingUploadError,
  showLine?: string
) {
  let errorText = ""

  if (showLine) {
    errorText +=
      (error.line_number ?? -1) >= 0
        ? t("Ligne {{lineNumber}} : ", { lineNumber: error.line_number })
        : ""
  }

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
      errorText += t("La matière première est manquante ou non reconnue (Verifiez la syntaxe dans la liste de matières premières qui est incluse dans le fichier excel).")
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
        "En {{year}}, les biocarburants issus d'effluents d'huilerie de palme et rafles ne seront pas reconnus au double comptage au delà d'une production total de 2000 tonnes par unité de production.",
        { year: error?.meta?.year }
      )
      break
    case DoubleCountingUploadErrorType.BadWorksheetName:
      errorText += t(
        "La feuille \"{{tabName}}\" n'a pas été trouvé dans le fichier. Vérifiez que la feuille n'est pas été renommée.",
        { tabName: error?.meta }
      )
      break
    case DoubleCountingUploadErrorType.ProductionMismatchQuota:
      errorText += t(
        "Le quota demandé dans l'onglet \"Reconnaissance double comptage\" ne peut pas être supérieur à la production prévisionelle renseignée ici.",
      )
      break
    case DoubleCountingUploadErrorType.LineFeedstocksIncoherent:
      errorText += t(
        "Les matières premières renseignées sur la même ligne doivent être identiques dans les deux tableaux.",
      )
      break
    case DoubleCountingUploadErrorType.UnknownYear:
      errorText += t(
        "Les années doivent être renseignées",
      )
      break

    default:
      errorText +=
        t("Erreur de validation") +
        `: ${error.error}${error.meta ? " " + error.meta : ""}`
      break
  }

  return errorText
}
