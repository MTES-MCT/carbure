import {
  DoubleCountingUploadError,
  DoubleCountingUploadErrorType,
} from "double-counting/types"
import { t } from "i18next"
import { c } from "msw/lib/glossary-de6278a9"

export function getErrorText(
  error: DoubleCountingUploadError,
  showLine: boolean = true
) {
  let errorText = ""

  if (showLine && (error.line_number ?? -1) >= 0) {
    errorText += t("Ligne {{lineNumber}}", { lineNumber: error.line_merged || error.line_number })
  }
  if (error.meta.tabName) {
    errorText += ` (${error.meta.tabName})`
  }

  if (errorText.length > 0)
    errorText += " : "

  switch (error.error) {
    case DoubleCountingUploadErrorType.UnkownFeedstock:
      errorText += t(
        "La matière première {{feedstock}} n'est pas reconnue. Vérifiez la syntaxe de ce code.",
        { feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }) }
      )
      break
    case DoubleCountingUploadErrorType.MissingData:
      errorText += t(
        "Les données n'ont pas étaient trouvées. Vérifiez que les données ont bien été renseignées.",
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
      errorText += t("Le biocarburant est manquant ou non reconnu.")
      break
    case DoubleCountingUploadErrorType.MissingFeedstock:
      errorText += t("En {{year}}, la matière première est manquante ou non reconnue (Verifiez la syntaxe dans la liste de matières premières qui est incluse dans le fichier excel).",
        { year: error.meta?.year })
      break
    case DoubleCountingUploadErrorType.MissingEstimatedProduction:
      errorText += t("En {{year}}, la production prévisionelle correspondante au couple \"{{biofuel}} / {{feedstock}}\" est manquante.", {
        year: error.meta?.year,
        feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }),
        biofuel: t(error.meta?.biofuel, { ns: "biofuels" }),
      })
      break
    case DoubleCountingUploadErrorType.MissingMaxProductionCapacity:
      errorText += t("En {{year}}, la capacité de production maximale correspondante au couple \"{{biofuel}} / {{feedstock}}\" est manquante.", {
        year: error.meta?.year,
        feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }),
        biofuel: t(error.meta?.biofuel, { ns: "biofuels" }),
      })
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
        "En {{year}}, les biocarburants issus d'effluents d'huilerie de palme et rafles (POME) ne peuvent pas être reconnus au double comptage au delà de 2000 tonnes par unité de production et par an.",
        { year: error?.meta?.year }
      )
      break
    case DoubleCountingUploadErrorType.BadWorksheetName:
      errorText += t(
        "La feuille \"{{sheetName}}\" n'a pas été trouvé dans le fichier. Vérifiez que la feuille n'est pas été renommée.",
        { sheetName: error?.meta.sheet_name }
      )
      break
    case DoubleCountingUploadErrorType.ProductionMismatchQuota:
      errorText += t(
        "En {{year}}, le quota demandé ({{requested_quota}} tonnes de {{biofuel}}) ne peut pas être supérieur à la production prévisionelle renseignée ({{estimated_production}} tonnes).",
        {
          year: error?.meta?.year,
          requested_quota: error?.meta?.requested_quota,
          biofuel: t(error.meta?.biofuel, { ns: "biofuels" }),
          estimated_production: error?.meta?.estimated_production
        }

      )
      break

    case DoubleCountingUploadErrorType.InvalidYear:
      errorText += t(
        "L'année renseignée ({{year}}) ne correspond pas à la période demandée. Vérifiez les années renseignées dans l'onglet \"Reconnaissance double comptage\".",
        { year: error?.meta.year }
      )
      break
    case DoubleCountingUploadErrorType.MissingPeriod:
      errorText += t(
        "La période de la demande n'a pas pu être trouvée sur le fichier. Vérifiez la première année de reconnaissance entrée en bas de l'onglet \"Reconnaissance double comptage\".",
        { year: error?.meta.year }
      )
      break
    case DoubleCountingUploadErrorType.UnknownYear:
      errorText += t(
        "Les années doivent être renseignées.",
      )
      break
    case DoubleCountingUploadErrorType.MissingCountryOfOrigin:
      errorText += t(
        "Le pays d'origine de la matière première {{feedstock}} doit être renseigné.",
        { feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }) }
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
