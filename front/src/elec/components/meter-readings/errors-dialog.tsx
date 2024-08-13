import { Button } from "common/components/button"
import Collapse from "common/components/collapse"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus, Return } from "common/components/icons"
import Tag from "common/components/tag"
import {
  ElecMeterReadingsApplicationCheckInfo,
} from "elec/types"
import { Trans, useTranslation } from "react-i18next"
import { t } from "i18next"
import { UploadCheckError } from "carbure/types"

export type MeterReadingsErrorsDetailsDialogProps = {
  fileData: ElecMeterReadingsApplicationCheckInfo
  onClose: () => void
}

export const MeterReadingsErrorsDetailsDialog = ({
  fileData,
  onClose,
}: MeterReadingsErrorsDetailsDialogProps) => {
  const { t } = useTranslation()

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <Tag big variant="warning">
          {t("À corriger")}
        </Tag>
        <h1>
          {t("Relevés trimestriels T{{quarter}} {{year}}", {
            quarter: fileData.quarter,
            year: fileData.year,
          })}
        </h1>
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
    case "extracted_energy":
      return t("Énergie active totale soutirée")
    case "reading_date":
      return t("Date du relevé")
    default:
      return t("Champ non reconnu")
  }
}

export default MeterReadingsErrorsDetailsDialog
