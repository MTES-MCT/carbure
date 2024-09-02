import { UploadCheckError, UploadCheckReportInfo } from "carbure/types"
import Button from "common/components/button"
import Collapse from "common/components/collapse"
import { AlertCircle, Return } from "common/components/icons"
import { t } from "i18next"
import { useTranslation } from "react-i18next"

const ReportErrorsSection = ({
  checkInfo,
  header,
  onCheckAgain,
}: {
  checkInfo: UploadCheckReportInfo
  header: JSX.Element
  onCheckAgain: () => void
}) => {
  const { t } = useTranslation()

  return (
    <>
      <main>
        {header}
        <section>
          <p>
            {t(
              "Le fichier {{fileName}} comporte {{errorCount}} incohérences. Veuillez les corriger puis recharger à nouveau votre fichier.",
              {
                fileName: checkInfo.file_name,
                errorCount: checkInfo.error_count,
              }
            )}
          </p>
        </section>
        <section>
          <ErrorsTable errors={checkInfo.errors!} />
        </section>
      </main>
      <footer>
        <Button
          icon={Return}
          label={t("Importer un nouveau fichier")}
          variant="primary"
          action={onCheckAgain}
        />
      </footer>
    </>
  )
}

export default ReportErrorsSection

type ErrorsTableProps = {
  errors: UploadCheckError[]
}

export const ErrorsTable = ({ errors }: ErrorsTableProps) => {
  const { t } = useTranslation()

  return (
    <Collapse
      icon={AlertCircle}
      variant="danger"
      label={t("{{errorCount}} erreurs", {
        errorCount: errors.length,
      })}
      isOpen
    >
      <section>
        <ul>
          {errors.map((error, index) => {
            return (
              <li key={`error-${index}`}>
                <b>{t("Ligne {{line}}", { line: error.line })}: </b>
                {getErrorText(error)}
              </li>
            )
          })}
        </ul>
      </section>
      <footer></footer>
    </Collapse>
  )
}

export function getErrorText(error: UploadCheckError) {
  switch (error.error) {
    case "EXCEL_PARSING_FAILED":
      return t(
        "Le fichier importé n'a pas pu être analysé. Merci de verifier que le format du modèle de fichier a bien été respecté."
      )

    case "INVALID_DATA":
      return (
        <ul>
          {Object.entries(error.meta).map(([field, errors]) => (
            <li>
              <b>{getFieldText(field)}:</b>
              <ul>
                {(errors as string[]).map((error) => (
                  <li>{error}</li>
                ))}
              </ul>
            </li>
          ))}
        </ul>
      )

    default:
      return (
        t("Erreur de validation") +
        `: ${error.error}${error.meta ? " " + error.meta : ""}`
      )
  }
}

function getFieldText(field: string) {
  switch (field) {
    case "charge_point_id":
      return t("Identifiant du point de recharge")
    case "observed_mid_or_prm_id":
      return t("Identifiant PRM ou MID constaté (si différent)")
    case "is_auditable":
      return t(
        "Infrastructure de recharge installée à la localisation renseignée"
      )
    case "has_dedicated_pdl":
      return t(
        "Identifiant renseigné visible à proximité immédiate de l'infrastructure"
      )
    case "current_type":
      return t("Type de courant électrique du point de recharge")
    case "audit_date":
      return t("Date du relevé par l'intervenant")
    case "observed_energy_reading":
      return t("Énergie active totale relevée")
    case "comment":
      return t("Limite dans la mission de contrôle")
  }
}
