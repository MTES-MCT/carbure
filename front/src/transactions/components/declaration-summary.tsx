import { useEffect } from "react"
import { Trans, useTranslation } from "react-i18next"
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
import dialogStyles from "common/components/dialog.module.css"
import { useNotificationContext } from "common/components/notifications"
import TransactionSummary from "./summary"
import usePeriod, { nextPeriod, prettyPeriod } from "common/hooks/use-period"
import { useMatomo } from "matomo"

type SummaryPromptProps = PromptProps<any> & {
  entityID: number
}

export const DeclarationSummaryPrompt = ({
  entityID,
  onResolve,
}: SummaryPromptProps) => {
  const matomo = useMatomo()
  const { t } = useTranslation()
  const notifications = useNotificationContext()

  const [summary, getSummary] = useAPI(api.getDeclarationSummary)
  const [validating, validateDeclaration] = useAPI(api.validateDeclaration)

  const period = usePeriod()
  const next = nextPeriod(period)

  async function askValidateDeclaration() {
    const ok = await confirm(
      t("Validation déclaration"),
      t(
        "Confirmez-vous que les informations fournies sont valides ? Vous ne pourrez plus modifier votre déclaration ultérieurement."
      )
    )

    if (ok) {
      const res = await validateDeclaration(entityID, period.year, period.month)

      if (res) {
        await getSummary(entityID, period.year, period.month)

        notifications.push({
          level: "success",
          text: t("Votre déclaration a bien été validée !"),
        })
      } else {
        notifications.push({
          level: "error",
          text: t("Votre déclaration n'a pas pu être validée !"),
        })
      }
    }
  }

  useEffect(() => {
    getSummary(entityID, period.year, period.month)
  }, [getSummary, entityID, period.year, period.month])

  const declaration = summary.data?.declaration
  const remaining = summary?.data?.remaining ?? 0

  const currentMonth = prettyPeriod(period)
  const nextMonth = prettyPeriod(next)

  return (
    <Dialog onResolve={onResolve} className={dialogStyles.dialogWide}>
      <DialogTitle text={t("Déclaration de durabilité")} />

      <span className={styles.declarationExplanation}>
        <Trans>
          Les tableaux suivants vous montrent un récapitulatif de vos entrées et
          sorties pour la période sélectionnée.
        </Trans>
      </span>

      <span className={styles.declarationExplanation}>
        <Trans>
          Afin d'être comptabilisés, les brouillons que vous avez créé pour
          cette période devront être envoyés avant la fin du mois suivant ladite
          période. Une fois la totalité de ces lots validés, vous pourrez
          vérifier ici l'état global de vos transactions et finalement procéder
          à la déclaration.
        </Trans>
      </span>

      <Box row className={styles.declarationPeriod}>
        <Button icon={ChevronLeft} onClick={period.prev} />
        <span className={styles.declarationPeriodText}>
          <Trans>
            Pour la période <b>{{ currentMonth }}</b>
          </Trans>
        </span>
        <Button icon={ChevronRight} onClick={period.next} />
      </Box>

      <TransactionSummary
        in={summary.data?.in ?? []}
        out={summary.data?.out ?? []}
      />

      <DialogButtons className={styles.declarationControls}>
        {!declaration?.declared && (
          <span className={styles.declarationDeadline}>
            {remaining === 0 && (
              <Trans>
                à valider avant la fin du mois de <b>{{ nextMonth }}</b>
              </Trans>
            )}
            {remaining > 0 && (
              <Trans count={remaining}>
                Encore <b>{{ remaining }} lots</b> en attente de validation pour
                cette période
              </Trans>
            )}
          </span>
        )}

        {declaration?.declared ? (
          <Button disabled level="success" icon={Check}>
            <Trans>Déclaration validée !</Trans>
          </Button>
        ) : (
          <AsyncButton
            disabled={summary?.data?.remaining !== 0}
            loading={validating.loading}
            level="primary"
            icon={Check}
            onClick={() => {
              matomo.push(["trackEvent", "transaction", "validate-declaration"])
              askValidateDeclaration()
            }}
          >
            <Trans>Valider ma déclaration</Trans>
          </AsyncButton>
        )}
        <Button icon={Return} onClick={() => onResolve()}>
          <Trans>Retour</Trans>
        </Button>
      </DialogButtons>

      {summary.loading && <LoaderOverlay />}
    </Dialog>
  )
}
