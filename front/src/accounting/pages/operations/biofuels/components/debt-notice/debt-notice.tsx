import { useDebts } from "accounting/hooks/use-debts"
import { Notice } from "common/components/notice"
import { useRoutes } from "common/hooks/routes"
import { useTranslation } from "react-i18next"

// Independent from the list filters: the debts are fetched on their own
export const DebtNotice = () => {
  const { t } = useTranslation()
  const routes = useRoutes()
  const { debts } = useDebts()

  if (debts.length === 0) return null

  return (
    <Notice
      variant="alert"
      isClosable
      title={
        debts.length === 1
          ? t("Vous avez une dette en cours")
          : t("Vous avez des dettes en cours")
      }
      linkText={t("Régulariser ma situation")}
      linkHref={routes.ACCOUNTING.BALANCES.BIOFUELS}
    />
  )
}
