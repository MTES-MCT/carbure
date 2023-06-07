import { Alert } from "common/components/alert"
import { Button } from "common/components/button"
import Collapse from "common/components/collapse"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus, Return } from "common/components/icons"
import Tabs from "common/components/tabs"
import Tag from "common/components/tag"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { getErrorText } from "settings/utils/double-counting"
import { DoubleCountingFileInfo, DoubleCountingUploadError } from "../../types"
import ApplicationInfo from "../application/application-info"
import { ProductionTable, SourcingFullTable } from "../dc-tables"

export type ErrorsDetailsDialogProps = {
  file: DoubleCountingFileInfo
  onClose: () => void
}

export const ErrorsDetailsDialog = ({
  file,
  onClose,
}: ErrorsDetailsDialogProps) => {
  const { t } = useTranslation()

  const [focus, setFocus] = useState("sourcing_forecast")

  const focusedErrors = file.errors?.[
    focus as keyof typeof file.errors
  ] as DoubleCountingUploadError[]

  return (
    <Dialog fullscreen onClose={onClose}>
      <header>
        <Tag big variant="warning">
          {t("A corriger")}
        </Tag>
        <h1>{t("Correction du dossier double comptage")}</h1>
      </header>

      <main>

        <ApplicationInfo file={file} />
        <section>
          <Tabs
            variant="switcher"
            tabs={[
              {
                key: "sourcing_forecast",
                label: `${t("Approvisionnement")} (${file.errors?.sourcing_forecast?.length || 0})`,
              },
              {
                key: "production",
                label: `${t("Production")} (${file.errors?.production?.length || 0})`,
              },
              {
                key: "global",
                label: `${t("Global")} (${file.errors?.global?.length || 0})`,
              },
            ]}
            focus={focus}
            onFocus={setFocus}
          />

          {focusedErrors.length === 0 && (
            <Alert variant="success" icon={AlertCircle}>
              <p>{t("Aucune erreur dans cet onglet")}</p>
            </Alert>
          )}

          {focusedErrors.length > 0 && <ErrorsTable errors={focusedErrors} />}

        </section>

        {focusedErrors.length === 0 && focus === "sourcing_forecast" &&
          <section>
            <SourcingFullTable
              sourcing={file.sourcing ?? []}
            />
          </section>
        }


        {focusedErrors.length === 0 && focus === "production" &&
          <section>
            <ProductionTable
              production={file.production ?? []}
            />
          </section>
        }
      </main>

      <footer>
        <Button
          icon={Plus}
          label={t("Ajouter le dossier")}
          variant="primary"
          disabled={true}
        />

        <Button icon={Return} label={t("Fermer")} action={onClose} asideX />
      </footer>

    </Dialog>
  )
}



type ErrorsTableProps = {
  errors: DoubleCountingUploadError[]
}

export const ErrorsTable = ({ errors }: ErrorsTableProps) => {
  const { t } = useTranslation()
  const errorFiltered = errors

  return <Collapse
    icon={AlertCircle}
    variant="warning"
    label={t("{{errorCount}} erreurs", {
      errorCount: errors.length,
    })}
    isOpen
  >
    <section>
      <ul>
        {errors.map((error, index) => {
          return <li key={`error-${index}`}>
            {error.line_number! >= 0
              && t("Ligne {{lineNumber}} : ", {
                lineNumber: error.line_merged || error.line_number,
              })}
            {getErrorText(error)}</li>
        })}
      </ul>
    </section>
    <footer></footer>
  </Collapse>

}


export default ErrorsDetailsDialog
