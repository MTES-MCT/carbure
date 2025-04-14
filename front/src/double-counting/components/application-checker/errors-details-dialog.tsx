import { Notice } from "common/components/notice"
import { Button } from "common/components/button2"
import { Collapse } from "common/components/collapse2"
import { Dialog } from "common/components/dialog2"
import { Tabs } from "common/components/tabs2"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import {
  DoubleCountingFileInfo,
  DoubleCountingUploadError,
  DoubleCountingUploadErrorType,
} from "../../types"
import FileApplicationInfo from "../../../double-counting-admin/components/files-checker/file-application-info"
import { SourcingFullTable } from "../sourcing-table"
import { ProductionTable } from "../production-table"
import { ProductionHistoryTable } from "../production-history-table"
import { t } from "i18next"
import { useMatch } from "react-router-dom"
import Badge from "@codegouvfr/react-dsfr/Badge"

export type ErrorsDetailsDialogProps = {
  fileData: DoubleCountingFileInfo
  onClose: () => void
}

export const ErrorsDetailsDialog = ({
  fileData,
  onClose,
}: ErrorsDetailsDialogProps) => {
  const { t } = useTranslation()
  const isProducerMatch = useMatch("/org/:entity/settings*")

  const [focus, setFocus] = useState("sourcing_forecast")

  const focusedErrors = fileData.errors?.[focus as keyof typeof fileData.errors]

  return (
    <Dialog
      fitContent
      onClose={onClose}
      header={
        <Dialog.Title>
          <Badge severity="warning">{t("À corriger")}</Badge>
          {t("Correction du dossier double comptage")}
        </Dialog.Title>
      }
      footer={
        <Button
          iconId={isProducerMatch ? "ri-send-plane-line" : "ri-add-line"}
          disabled
        >
          {isProducerMatch ? t("Envoyer la demande") : t("Ajouter le dossier")}
        </Button>
      }
    >
      <FileApplicationInfo fileData={fileData} />

      <Notice variant="warning" icon="ri-error-warning-line">
        {t(
          `{{count}} erreurs ont été détectées dans le fichier Excel source. Merci de corriger le fichier et envoyez-le à nouveau.`,
          { count: fileData.error_count }
        )}
      </Notice>

      <Tabs
        tabs={[
          {
            key: "sourcing_forecast",
            label: `${t("Approvisionnement")} (${fileData.errors?.sourcing_forecast?.length || 0})`,
            icon: "ri-profile-line",
            iconActive: "ri-profile-fill",
          },
          {
            key: "production",
            label: `${t("Production")} (${fileData.errors?.production?.length || 0})`,
            icon: "ri-user-line",
            iconActive: "ri-user-fill",
          },
          {
            key: "sourcing_history",
            label: `${t("Historique d'approvisionnement")} (${fileData.errors?.sourcing_history?.length || 0})`,
            icon: "ri-history-line",
          },
          {
            key: "production_history",
            label: `${t("Historique de production")} (${fileData.errors?.production_history?.length || 0})`,
            icon: "ri-history-line",
          },
          {
            key: "global",
            label: `${t("Global")} (${fileData.errors?.global_errors?.length || 0})`,
            icon: "ri-global-line",
          },
        ]}
        focus={focus}
        onFocus={setFocus}
        sticky
      />

      {focusedErrors.length === 0 && (
        <Notice
          variant="info"
          icon="fr-icon-success-line"
          title={t("Aucune erreur dans cet onglet")}
        ></Notice>
      )}

      {focusedErrors.length > 0 && <ErrorsTable errors={focusedErrors} />}

      {focusedErrors.length === 0 && focus === "sourcing_forecast" && (
        <SourcingFullTable sourcing={fileData.sourcing ?? []} />
      )}

      {focusedErrors.length === 0 && focus === "production" && (
        <ProductionTable
          production={fileData.production ?? []}
          sourcing={fileData.sourcing}
        />
      )}

      {focusedErrors.length === 0 && focus === "sourcing_history" && (
        <SourcingFullTable sourcing={fileData.sourcing_history ?? []} />
      )}

      {focusedErrors.length === 0 && focus === "production_history" && (
        <ProductionHistoryTable
          production={fileData.production_history ?? []}
        />
      )}
    </Dialog>
  )
}

type ErrorsTableProps = {
  errors: DoubleCountingUploadError[]
}

export const ErrorsTable = ({ errors }: ErrorsTableProps) => {
  const { t } = useTranslation()

  return (
    <Collapse
      icon="ri-error-warning-line"
      label={t("{{count}} erreurs", {
        count: errors.length,
      })}
      defaultExpanded
    >
      <section>
        <ul>
          {errors.map((error, index) => {
            return <li key={`error-${index}`}>{getErrorText(error)}</li>
          })}
        </ul>
      </section>
      <footer></footer>
    </Collapse>
  )
}

export default ErrorsDetailsDialog

export function getErrorText(
  error: DoubleCountingUploadError,
  showLine = true
) {
  let errorText = ""

  if (showLine && (error.line_number ?? -1) >= 0) {
    errorText += t("Ligne {{lineNumber}}", {
      lineNumber: error.line_merged || error.line_number,
    })
  }
  if (error.meta.tab_name) {
    errorText += ` (${error.meta.tab_name})`
  }

  if (errorText.length > 0) errorText += " : "

  switch (error.error) {
    case DoubleCountingUploadErrorType.MissingData:
      errorText += t(
        "Les données n'ont pas étaient trouvées. Vérifiez que les données ont bien été renseignées.",
        { feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }) }
      )
      break
    case DoubleCountingUploadErrorType.MissingBiofuel:
      errorText += t("Le biocarburant est manquant ou non reconnu.")
      break
    case DoubleCountingUploadErrorType.MissingFeedstock:
      errorText += t(
        "En {{year}}, la matière première est manquante ou non reconnue (Verifiez la syntaxe dans la liste de matières premières qui est incluse dans le fichier excel).",
        { year: error.meta?.year }
      )
      break
    case DoubleCountingUploadErrorType.MissingEstimatedProduction:
      errorText += t(
        'En {{year}}, la production prévisionelle correspondante au couple "{{biofuel}} / {{feedstock}}" est manquante.',
        {
          year: error.meta?.year,
          feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }),
          biofuel: t(error.meta?.biofuel, { ns: "biofuels" }),
        }
      )
      break
    case DoubleCountingUploadErrorType.MissingMaxProductionCapacity:
      errorText += t(
        'En {{year}}, la capacité de production maximale correspondante au couple "{{biofuel}} / {{feedstock}}" est manquante.',
        {
          year: error.meta?.year,
          feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }),
          biofuel: t(error.meta?.biofuel, { ns: "biofuels" }),
        }
      )
      break
    case DoubleCountingUploadErrorType.FeedstockNotDoubleCounting:
      errorText += t(
        "La matière première {{feedstock}} n'est pas comprise dans la liste des matières premières pouvant être double comptées.",
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
          estimated_production: error?.meta?.estimated_production,
        }
      )
      break
    case DoubleCountingUploadErrorType.ProductionMismatchProductionMax:
      errorText += t(
        "En {{year}}, la capacité de production maximale de {{feedstock}} ({{maxProductionCapacity}} tonnes) doit être supérieur aux {{estimatedProduction}} tonnes de {{biofuel}} estimés.",
        {
          year: error.meta?.year,
          feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }),
          maxProductionCapacity: error?.meta?.max_production_capacity,
          estimatedProduction: error?.meta?.estimated_production,
          biofuel: t(error.meta?.biofuel, { ns: "biofuels" }),
        }
      )

      break

    case DoubleCountingUploadErrorType.InvalidYear:
      errorText += t(
        "L'année renseignée ({{year}}) ne correspond pas à la période demandée. Vérifiez les années renseignées dans l'onglet \"Reconnaissance double comptage\".",
        { year: error?.meta.year }
      )
      break
    case DoubleCountingUploadErrorType.UnknownYear:
      errorText += t(
        'Les années doivent être renseignées. Vérifiez que la première année de reconnaissance soit entrée en bas de l\'onglet "Reconnaissance double comptage".'
      )
      break
    case DoubleCountingUploadErrorType.MissingCountryOfOrigin:
      errorText += t(
        "Le pays d'origine de la matière première {{feedstock}} doit être renseigné.",
        { feedstock: t(error.meta?.feedstock, { ns: "feedstocks" }) }
      )
      break
    case DoubleCountingUploadErrorType.UnknownCountryOfOrigin:
      errorText += t(
        "Le pays d'origine de la matière première {{feedstock}} n'est pas reconnue. Merci de verifier la syntaxe dans la liste des pays d'origine qui est incluse dans le fichier excel",
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
