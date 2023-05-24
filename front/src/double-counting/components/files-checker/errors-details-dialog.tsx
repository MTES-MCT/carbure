import { Alert } from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Return } from "common/components/icons"
import Table, { Cell, Column } from "common/components/table"
import Tabs from "common/components/tabs"
import Tag from "common/components/tag"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { getErrorText } from "settings/utils/double-counting"
import { DoubleCountingFileInfo, DoubleCountingUploadError } from "../../types"

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
        <h1>{t("Vérification du dossier")} </h1>
      </header>

      <main>
        <section>
          <p>
            <Trans
              values={{
                fileName: file.file_name,
                productionSite: file.production_site,
              }}
              defaults="Voici la liste des erreurs identifiées dans le fichier <b>{{fileName}}</b> pour le site de production <b>{{productionSite}}</>."
            />
          </p>
        </section>

        <section>
          <Tabs
            variant="switcher"
            tabs={[
              {
                key: "sourcing_forecast",
                label: t("Approvisionnement ({{errorCount}})", {
                  errorCount: file.errors?.sourcing_forecast?.length || 0,
                }),
              },
              // {
              //   key: "sourcing_history",
              //   label: t("Historique d'appro. ({{errorCount}})", {
              //     errorCount: file.errors?.sourcing_history?.length || 0,
              //   }),
              // },
              {
                key: "production",
                label: t("Production ({{errorCount}})", {
                  errorCount: file.errors?.production?.length || 0,
                }),
              },
              {
                key: "global",
                label: t("Global ({{errorCount}})", {
                  errorCount: file.errors?.global?.length || 0,
                }),
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
      </main>

      <footer>
        <Button icon={Return} action={onClose}>
          <Trans>Retour</Trans>
        </Button>
      </footer>
    </Dialog>
  )
}

type ErrorsTableProps = {
  errors: DoubleCountingUploadError[]
}

export const ErrorsTable = ({ errors }: ErrorsTableProps) => {
  const { t } = useTranslation()
  const errorFiltered = errors //mergeErrors(errors)

  const columns: Column<DoubleCountingUploadError>[] = [
    {
      header: t("Ligne"),
      style: { width: 120, flex: "none" },
      cell: (error) => (
        <p>
          {error.line_number! >= 0
            ? t("Ligne {{lineNumber}}", {
                lineNumber: error.line_merged || error.line_number,
              })
            : "-"}
        </p>
      ),
    },
    {
      header: t("Erreur"),
      cell: (error) => <p>{getErrorText(error)}</p>,
    },
  ]

  return <Table columns={columns} rows={errorFiltered} />
}

const mergeErrors = (errors: DoubleCountingUploadError[]) => {
  const errorsMergedByError: DoubleCountingUploadError[] = []
  errors
    .sort((a, b) => a.error.localeCompare(b.error))
    .forEach((error, index) => {
      if (index === 0) {
        error.line_merged = error.line_number?.toString() || ""
        errorsMergedByError.push(error)
        return
      }
      const prevError = errorsMergedByError[errorsMergedByError.length - 1]

      if (error.error === prevError.error) {
        prevError.line_merged = prevError.line_merged + ", " + error.line_number
        return
      }
      error.line_merged = error.line_number?.toString() || ""
      errorsMergedByError.push(error)
    })
  return errorsMergedByError
}

export default ErrorsDetailsDialog
