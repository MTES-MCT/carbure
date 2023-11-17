import { Alert } from "common/components/alert"
import { Button } from "common/components/button"
import Collapse from "common/components/collapse"
import { Dialog } from "common/components/dialog"
import { AlertCircle, AlertTriangle, Plus, Return } from "common/components/icons"
import Tag from "common/components/tag"
import { ChargingPointsSubscriptionError, ElecChargingPointsSubscriptionCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { t } from "i18next"

export type ErrorsDetailsDialogProps = {
  fileData: ElecChargingPointsSubscriptionCheckInfo
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
  errors: ChargingPointsSubscriptionError[]
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
  error: ChargingPointsSubscriptionError,
) {
  console.log('error:', error)


  switch (error.error) {

    case "MISSING_CHARGING_POINT_IN_DATAGOUV":
      return t(
        "Les identifiants de points de recharge suivants n'existent pas dans la consolidation transport.data.gouv : {{chargingPoints}}",
        { chargingPoints: error.meta?.charging_points.join(",") }
      )

    case "MISSING_CHARGING_POINT_DATA":
      return t(
        "Les informations relatives aux relevés (date_releve, releve, no_mid) sont manquantes ou pas correctement remplies pour les points de recharge suivants :",
        { chargingPoints: error.meta?.charging_points.join(",") }
      )

    default:
      return t("Erreur de validation") +
        `: ${error.error}${error.meta ? " " + error.meta : ""}`

  }

}
