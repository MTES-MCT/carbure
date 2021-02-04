import { useEffect, useState } from "react"
import Table, { Column, Line } from "common/components/table"
import useAPI from "common/hooks/use-api"
import { SummaryItem } from "common/types"
import { padding } from "./list-columns"
import * as api from "../api"
import { Alert } from "common/components/alert"
import {
  AlertCircle,
  Check,
  ChevronLeft,
  ChevronRight,
  Return,
} from "common/components/icons"
import {
  confirm,
  DialogButtons,
  PromptFormProps,
} from "common/components/dialog"
import { AsyncButton, Button } from "common/components/button"
import { Box, LoaderOverlay, Title } from "common/components"
import styles from "./declaration-summary.module.css"
import colStyles from "./list-columns.module.css"
import { useNotificationContext } from "common/components/notifications"

const COLUMNS: Column<SummaryItem>[] = [
  {
    header: "Biocarburant",
    render: (d) => <Line text={d.biocarburant} />,
  },
  {
    header: "Volume (litres)",
    render: (d) => <Line text={`${d.volume}`} />,
  },
  {
    header: "Lots",
    className: colStyles.narrowColumn,
    render: (d) => <Line text={`${d.lots}`} />,
  },
  {
    header: "Réd. GES",
    className: colStyles.narrowColumn,
    render: (d) => <Line text={`${d.avg_ghg_reduction.toFixed(2)}%`} />,
  },
  padding,
]

const now = new Date()

function prevPeriod(period: { year: number; month: number }) {
  const month = period.month === 1 ? 12 : period.month - 1
  const year = period.month === 1 ? period.year - 1 : period.year
  return { year, month }
}

function nextPeriod(period: { year: number; month: number }) {
  const month = period.month === 12 ? 1 : period.month + 1
  const year = period.month === 12 ? period.year + 1 : period.year
  return { year, month }
}

export const SummaryPromptFactory = (entityID: number) =>
  function SummaryPrompt({ onCancel }: PromptFormProps<any>) {
    const notifications = useNotificationContext()

    const [summary, getSummary] = useAPI(api.getDeclarationSummary)
    const [validating, validateDeclaration] = useAPI(api.validateDeclaration)

    const [period, setPeriod] = useState({
      year: now.getFullYear(),
      month: now.getMonth() + 1,
    })

    async function askValidateDeclaration() {
      const ok = await confirm(
        "Validation déclaration",
        "Confirmez-vous que les informations fournies sont valides ? Vous ne pourrez plus modifier votre déclaration ultérieurement."
      )

      if (ok) {
        try {
          await validateDeclaration(entityID, period.year, period.month)
          await getSummary(entityID, period.year, period.month)

          notifications.push({
            level: "success",
            text: "Votre déclaration a bien été validée !",
          })
        } catch (e) {
          notifications.push({
            level: "error",
            text: "Votre déclaration n'a pas pu être validée !",
          })
        }
      }
    }

    useEffect(() => {
      getSummary(entityID, period.year, period.month)
    }, [getSummary, period])

    const declaration = summary.data?.declaration
    const summaryInRows = (summary.data?.in ?? []).map((v) => ({ value: v }))
    const summaryOutRows = (summary.data?.out ?? []).map((v) => ({ value: v }))

    const isInEmpty = summaryInRows.length === 0
    const isOutEmpty = summaryOutRows.length === 0

    const inColumns: Column<SummaryItem>[] = [
      padding,
      {
        header: "Fournisseur",
        render: (d) => <Line text={d.entity} />,
      },
      ...COLUMNS,
    ]

    const outColumns: Column<SummaryItem>[] = [
      padding,
      {
        header: "Client",
        render: (d) => <Line text={d.entity} />,
      },
      ...COLUMNS,
    ]

    return (
      <Box className={styles.declarationContent}>
        <span className={styles.declarationExplanation}>
          Vous avez jusqu'à la fin du mois pour valider l'ensemble de vos lots
          pour le mois précédent. Une fois que vous aurez validé la totalité de
          vos lots pour le mois précédent, vous pourrez les déclarer.
        </span>

        <Box row className={styles.declarationPeriod}>
          <Button
            onClick={() => setPeriod(prevPeriod)}
            className={styles.declarationPrevPeriod}
          >
            <ChevronLeft />
          </Button>
          <span className={styles.declarationPeriodText}>
            Pour la période{" "}
            <b>
              {/* pad month with leading 0 */}
              {("0" + period.month).slice(-2)} / {period.year}
            </b>
          </span>
          <Button
            onClick={() => setPeriod(nextPeriod)}
            className={styles.declarationNextPeriod}
          >
            <ChevronRight />
          </Button>
        </Box>

        {isInEmpty && isOutEmpty && (
          <Alert level="warning" icon={AlertCircle}>
            Aucune information trouvée pour la période donnée.
          </Alert>
        )}

        {!isInEmpty && (
          <Box className={styles.declarationSummary}>
            <Title className={styles.declarationSection}>Entrées</Title>
            <Table
              columns={inColumns}
              rows={summaryInRows}
              className={styles.declarationTable}
            />
          </Box>
        )}

        <br />

        {!isOutEmpty && (
          <Box className={styles.declarationSummary}>
            <Title className={styles.declarationSection}>Sorties</Title>
            <Table
              columns={outColumns}
              rows={summaryOutRows}
              className={styles.declarationTable}
            />
          </Box>
        )}

        <DialogButtons className={styles.declarationControls}>
          {declaration?.declared ? (
            <Button disabled level="success" icon={Check}>
              Déclaration validée !
            </Button>
          ) : (
            <AsyncButton
              loading={validating.loading}
              disabled={isInEmpty && isOutEmpty}
              level="primary"
              icon={Check}
              onClick={askValidateDeclaration}
            >
              Valider ma déclaration
            </AsyncButton>
          )}
          <Button icon={Return} onClick={onCancel}>
            Retour
          </Button>
        </DialogButtons>

        {summary.loading && <LoaderOverlay />}
      </Box>
    )
  }
