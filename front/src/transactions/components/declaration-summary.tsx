import { useEffect, useState } from "react"
import useAPI from "common/hooks/use-api"
import * as api from "../api"
import {
  Check,
  ChevronLeft,
  ChevronRight,
  Return,
} from "common/components/icons"
import {
  confirm,
  Dialog,
  DialogButtons,
  DialogTitle,
  PromptProps,
} from "common/components/dialog"
import { AsyncButton, Button } from "common/components/button"
import { Box, LoaderOverlay } from "common/components"
import styles from "./declaration-summary.module.css"
import { useNotificationContext } from "common/components/notifications"
import TransactionSummary from "./transaction-summary"

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

type SummaryPromptProps = PromptProps<any> & {
  entityID: number
}

export const SummaryPrompt = ({ entityID, onResolve }: SummaryPromptProps) => {
  const notifications = useNotificationContext()

  const [summary, getSummary] = useAPI(api.getDeclarationSummary)
  const [validating, validateDeclaration] = useAPI(api.validateDeclaration)

  const [period, setPeriod] = useState(
    prevPeriod({
      year: now.getFullYear(),
      month: now.getMonth() + 1,
    })
  )

  const next = nextPeriod(period)

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

  return (
    <Dialog onResolve={onResolve}>
      <DialogTitle text="Déclaration de durabilité" />

      <Box className={styles.declarationContent}>
        <span className={styles.declarationExplanation}>
          Les tableaux suivants vous montrent un récapitulatif de vos entrées et
          sorties pour la période sélectionnée.
        </span>

        <span className={styles.declarationExplanation}>
          Afin d'être comptabilisés, les brouillons que vous avez créé pour
          cette période devront être envoyés avant la fin du mois suivant ladite
          période. Une fois la totalité de ces lots validés, vous pourrez
          vérifier ici l'état global de vos transactions et finalement procéder
          à la déclaration.
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

        <TransactionSummary
          in={summary.data?.in ?? []}
          out={summary.data?.out ?? []}
        />

        <DialogButtons className={styles.declarationControls}>
          <span className={styles.declarationDeadline}>
            à valider avant la fin du mois de{" "}
            <b>
              {("0" + next.month).slice(-2)} / {next.year}
            </b>
          </span>

          {declaration?.declared ? (
            <Button disabled level="success" icon={Check}>
              Déclaration validée !
            </Button>
          ) : (
            <AsyncButton
              loading={validating.loading}
              level="primary"
              icon={Check}
              onClick={askValidateDeclaration}
            >
              Valider ma déclaration
            </AsyncButton>
          )}
          <Button icon={Return} onClick={() => onResolve()}>
            Retour
          </Button>
        </DialogButtons>

        {summary.loading && <LoaderOverlay />}
      </Box>
    </Dialog>
  )
}
