import { Button } from "common/components/button"
import Collapse from "common/components/collapse"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus, Return } from "common/components/icons"
import Tag from "common/components/tag"
import {
  ChargingPointsApplicationError,
  ElecChargingPointsApplicationCheckInfo,
  ElecMeterReadingsApplicationCheckInfo,
} from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { t } from "i18next"

export type MeterReadingsErrorsDetailsDialogProps = {
  fileData: ElecMeterReadingsApplicationCheckInfo
  onClose: () => void
  quarterString: string
}

export const MeterReadingsErrorsDetailsDialog = ({
  fileData,
  onClose,
  quarterString,
}: MeterReadingsErrorsDetailsDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <Tag big variant="warning">
          {t("À corriger")}
        </Tag>
        <h1>{t("Relevés trimestriels {{quarter}}", { quarter: quarterString })}</h1>
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
          label={t("Transmettre mes relevés trimestriels")}
          variant="primary"
          disabled={true}
        />

        <Button icon={Return} label={t("Charger un nouveau fichier")} action={onClose} asideX />
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
    case "EXCEL_PARSING_FAILED":
      return t("Le fichier importé n'a pas pu être analysé. Merci de verifier que le format du modèle de fichier a bien été respecté.")

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
    case "mid_id":
      return t("Identifiant MID")
    default:
      return "Champ non reconnu"
  }
}

export default MeterReadingsErrorsDetailsDialog
