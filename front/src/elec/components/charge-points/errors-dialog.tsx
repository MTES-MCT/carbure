import { Button } from "common/components/button"
import Collapse from "common/components/collapse"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus, Return } from "common/components/icons"
import Tag from "common/components/tag"
import { ElecChargePointsApplicationCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { t } from "i18next"
import { TDGInfo } from "./tdg-info"
import { UploadCheckError } from "common/types"

export type ErrorsDetailsDialogProps = {
  fileData: ElecChargePointsApplicationCheckInfo
  onClose: () => void
}

export const ErrorsDetailsDialog = ({
  fileData,
  onClose,
}: ErrorsDetailsDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <Tag big variant="warning">
          {t("À corriger")}
        </Tag>
        <h1>{t("Inscription des points de recharge")}</h1>
      </header>

      <main>
        <section>
          <p style={{ textAlign: "left" }}>
            <Trans
              defaults="Le fichier <b>{{fileName}}</b> comporte <b>{{count}} incohérences</b>.  Veuillez les corriger puis recharger à nouveau votre fichier."
              values={{ fileName: fileData.file_name }}
              count={fileData.error_count}
            />
          </p>
        </section>

        <section>
          <TDGInfo />
        </section>

        <section>
          <ErrorsTable errors={fileData.errors!} />
        </section>
      </main>

      <footer>
        <Button
          icon={Plus}
          label={t("Envoyer la demande d'inscription")}
          variant="primary"
          disabled={true}
        />

        <Button
          icon={Return}
          label={t("Charger un nouveau fichier")}
          action={onClose}
          asideX
        />
      </footer>
    </Dialog>
  )
}

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
    case "current_type":
      return t("Type de courant")
    case "installation_date":
      return t("Date d'installation")
    case "mid_id":
      return t("Identifiant MID")
    case "measure_date":
      return t("Date du relevé")
    case "measure_energy":
      return t("Énergie soutirée")
    case "is_article_2":
      return t("Soumis à l'article 2")
    case "is_auto_consumption":
      return t("Auto-consommation")
    case "is_article_4":
      return t("Soumis à l'article 4")
    case "measure_reference_point_id":
      return t("Point de référence mesure")

    default:
      return "Champ non reconnu"
  }
}

export default ErrorsDetailsDialog
