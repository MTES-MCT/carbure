import { Alert } from "common/components/alert"
import { Button } from "common/components/button"
import { Dialog } from "common/components/dialog"
import { AlertCircle, Plus, Return } from "common/components/icons"
import Tabs from "common/components/tabs"
import Tag from "common/components/tag"
import { useState } from "react"
import { Trans, useTranslation } from "react-i18next"
import { getErrorText } from "settings/utils/double-counting"
import { DoubleCountingFileInfo, DoubleCountingSourcing, DoubleCountingSourcingAggregation, DoubleCountingUploadError } from "../../types"
import { ProductionTable, SourcingAggregationTable, SourcingTable } from "../dc-tables"
import Collapse from "common/components/collapse"
import Checkbox from "common/components/checkbox"
import { t } from "i18next"

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
                productionSite: file.production_site,
              }}
              defaults={`Pour le site de production <b>{{productionSite}}</b> par `}
            /><a href={`mailto:${file.producer_email}`}>{file.producer_email}</a>.
          </p>
          <p>
            <Trans
              values={{
                fileName: file.file_name,
              }}
              defaults="Fichier excel téléchargé : <b>{{fileName}}</b>"
            />
          </p>
          <p>
            <Trans
              values={{
                period: `${file.year} - ${file.year + 1}`,
              }}
              defaults="Période demandée : <b>{{period}}</b>"
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

        {focus === "sourcing_forecast" &&
          <section>
            <SourcingFullTable
              sourcing={file.sourcing ?? []}
            />
          </section>
        }


        {focus === "production" &&
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

const SourcingFullTable = ({ sourcing }: { sourcing: DoubleCountingSourcing[] }) => {

  const [aggregateSourcing, setAggregateSourcing] = useState(true);

  const aggregateDoubleCountingSourcing = (data: DoubleCountingSourcing[]): DoubleCountingSourcingAggregation[] => {
    const aggregationMap = new Map<string, DoubleCountingSourcingAggregation>();
    for (const item of data) {
      const key = `${item.feedstock.code}_${item.year}`;
      const aggregation = aggregationMap.get(key);

      if (aggregation) {
        aggregation.sum += item.metric_tonnes;
        aggregation.count += 1;
      } else {
        aggregationMap.set(key, {
          year: item.year,
          sum: item.metric_tonnes,
          count: 1,
          feedstock: item.feedstock
        });
      }
    }

    return Array.from(aggregationMap.values());
  }

  const aggregated_sourcing: DoubleCountingSourcingAggregation[] = aggregateDoubleCountingSourcing(sourcing);

  return <>

    <Checkbox readOnly value={aggregateSourcing} onChange={() => setAggregateSourcing(!aggregateSourcing)}>
      {t("Agréger les données d’approvisionnement par matière première ")}
    </Checkbox>
    {!aggregateSourcing &&
      <SourcingTable
        sourcing={sourcing ?? []}
      />
    }
    {aggregateSourcing &&
      <SourcingAggregationTable
        sourcing={aggregated_sourcing ?? []}
      />
    }
  </>
}

type ErrorsTableProps = {
  errors: DoubleCountingUploadError[]
}

export const ErrorsTable = ({ errors }: ErrorsTableProps) => {
  const { t } = useTranslation()
  const errorFiltered = errors //mergeErrors(errors)

  // const columns: Column<DoubleCountingUploadError>[] = [
  //   {
  //     header: t("Ligne"),
  //     style: { width: 120, flex: "none" },
  //     cell: (error) => (
  //       <p>
  //         {error.line_number! >= 0
  //           ? t("Ligne {{lineNumber}}", {
  //             lineNumber: error.line_merged || error.line_number,
  //           })
  //           : "-"}
  //       </p>
  //     ),
  //   },
  //   {
  //     header: t("Erreur"),
  //     cell: (error) => <p>{getErrorText(error)}</p>,
  //   },
  // ]
  // return <Table columns={columns} rows={errorFiltered} />

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

// const mergeErrors = (errors: DoubleCountingUploadError[]) => {
//   const errorsMergedByError: DoubleCountingUploadError[] = []
//   errors
//     .sort((a, b) => a.error.localeCompare(b.error))
//     .forEach((error, index) => {
//       if (index === 0) {
//         error.line_merged = error.line_number?.toString() || ""
//         errorsMergedByError.push(error)
//         return
//       }
//       const prevError = errorsMergedByError[errorsMergedByError.length - 1]

//       if (error.error === prevError.error) {
//         prevError.line_merged = prevError.line_merged + ", " + error.line_number
//         return
//       }
//       error.line_merged = error.line_number?.toString() || ""
//       errorsMergedByError.push(error)
//     })
//   return errorsMergedByError
// }

export default ErrorsDetailsDialog
