import { Alert } from "common/components/alert"
import { Button } from "common/components/button"
import Collapse from "common/components/collapse"
import { Dialog } from "common/components/dialog"
import { AlertCircle, AlertTriangle, Plus, Return } from "common/components/icons"
import Tag from "common/components/tag"
import { ChargingPointsSubscriptionError, ElecChargingPointsSubscriptionCheckInfo } from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { getErrorText } from "settings/utils/double-counting"

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
            `dzadza
            <Trans defaults="Le fichier <b>{{fileName}}</b> comporte {{count}} incohérences.  Veuillez les corriger puis recharger à nouveau votre fichier."
              fileName={fileData.file_name} count={fileData.error_count} />
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
            {error.error}</li>
        })}
      </ul>
    </section>
    <footer></footer>
  </Collapse>

}


export default ErrorsDetailsDialog
