import { useDebts } from "accounting/hooks/use-debts"
import { Alert } from "common/components/alert2"
import { Button } from "common/components/button2"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"

// Independent from the list filters: the debts are fetched on their own
export const DebtNotice = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { debts } = useDebts()

  if (debts.length === 0) return null

  return (
    <Alert
      severity="error"
      closable
      small
      description={
        <p>
          {t("Vous avez {{count}} dette en cours", {
            count: debts.length,
          })}
          <Button
            style={{ marginLeft: "var(--spacing-1w)" }}
            customPriority="link"
            linkProps={{ to: routes.ACCOUNTING.BALANCES.BIOFUELS }}
          >
            {t("Régulariser ma situation")}
          </Button>
        </p>
      }
    />
  )
}
