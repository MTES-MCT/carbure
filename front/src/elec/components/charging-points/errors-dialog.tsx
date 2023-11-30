import { Alert } from "common/components/alert"
import { Button } from "common/components/button"
import Collapse from "common/components/collapse"
import { Dialog } from "common/components/dialog"
import { AlertCircle, AlertTriangle, Plus, Return } from "common/components/icons"
import Tag from "common/components/tag"
import { ChargingPointsApplicationError, ElecChargingPointsApplicationCheckInfo } from "elec/types"
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
          <p style={{ textAlign: 'left' }}>
            <Trans defaults="Le fichier <b>{{fileName}}</b> comporte <b>{{count}} incohérences</b>.  Veuillez les corriger puis recharger à nouveau votre fichier."
              values={{ fileName: fileData.file_name }} count={fileData.error_count} />
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

  return <Collapse
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
          return <li key={`error-${index}`}>
            {getErrorText(error)}</li>
        })}
      </ul>
    </section>
    <footer></footer>
  </Collapse>

}


export default ErrorsDetailsDialog



export function getErrorText(
  error: ChargingPointsApplicationError,
) {

  switch (error.error) {

    case "MISSING_CHARGING_POINT_IN_DATAGOUV":
      return t(
        "Ligne {{line}}: L'identifiant du point de recharge n'existe pas sur transport.data.gouv : \"{{chargingPointId}}\"",
        { line: error.line, chargingPointId: error.meta }
      )

    case "MISSING_CHARGING_POINT_DATA":
      return t(
        "Ligne {{line}}: Certaines informations relatives aux relevés sont manquantes: {{missingFields}}",
        { line: error.line, missingFields: error.meta?.join(",") }
      )

    default:
      return t("Ligne {{line}}: Erreur de validation", { line: error.line }) +
        `: ${error.error}${error.meta ? " " + error.meta : ""}`

  }

}
