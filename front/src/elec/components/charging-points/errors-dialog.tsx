import { Button } from "common/components/button"
import Collapse from "common/components/collapse"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus, Return } from "common/components/icons"
import Tag from "common/components/tag"
import {
  ChargingPointsApplicationError,
  ElecChargingPointsApplicationCheckInfo,
} from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { t } from "i18next"

export type ErrorsDetailsDialogProps = {
  fileData: ElecChargingPointsApplicationCheckInfo
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
          {t("A corriger")}
        </Tag>
        <h1>{t("Correction du dossier double comptage")}</h1>
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

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>
    </Dialog>
  )
}

type ErrorsTableProps = {
  errors: ChargingPointsApplicationError[]
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

export function getErrorText(error: ChargingPointsApplicationError) {
  switch (error.error) {
    case "MISSING_CHARGING_POINT_ID":
      return t("L'identifiant du point de recharge n'est pas renseigné")

    case "MISSING_CHARGING_POINT_IN_DATAGOUV":
      return t(
        `L'identifiant "{{chargingPointId}}" du point de recharge n'existe pas sur transport.data.gouv.fr`,
        { chargingPointId: error.meta }
      )

    case "MISSING_CHARGING_POINT_DATA":
      return t(`Le champ "{{missingField}}" n'est pas renseigné`, {
        missingField: getFieldText(error.meta),
      })

    case "INVALID_CHARGING_POINT_DATA":
      return t(`Le champ "{{invalidField}}" est invalide`, {
        invalidField: getFieldText(error.meta),
      })

    default:
      return (
        t("Erreur de validation") +
        `: ${error.error}${error.meta ? " " + error.meta : ""}`
      )
  }
}

function getFieldText(field: string) {
  switch (field) {
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
