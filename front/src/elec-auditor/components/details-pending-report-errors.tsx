import { UploadCheckError, UploadCheckReportInfo } from "carbure/types"
import Button from "common/components/button"
import Collapse from "common/components/collapse"
import { AlertCircle, Return } from "common/components/icons"
import { useTranslation } from "react-i18next"


const ReportErrorsSection = ({ checkInfo, header, onCheckAgain }: {
  checkInfo: UploadCheckReportInfo,
  header: JSX.Element,
  onCheckAgain: () => void
}) => {
  const { t } = useTranslation()

  return <>
    <main>
      {header}
      <section>
        <p>{t("Le fichier {{fileName}} comporte {{errorCount}} incohérences. Veuillez les corriger puis recharger à nouveau votre fichier.", { fileName: checkInfo.file_name, errorCount: checkInfo.error_count })}</p>
      </section>
      <section>
        <ErrorsTable errors={checkInfo.errors!} />
      </section>
    </main>
    <footer>
      <Button icon={Return} label={t("Importer un nouveau fichier")} variant="primary" action={onCheckAgain} />
    </footer>
  </>
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
                <p> {error.error}</p>
              </li>
            )
          })}
        </ul>
      </section>
      <footer></footer>
    </Collapse>
  )
}
