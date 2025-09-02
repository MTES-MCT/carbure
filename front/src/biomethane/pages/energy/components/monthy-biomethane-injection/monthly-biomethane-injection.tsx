import { useTranslation } from "react-i18next"
import { EditableCard } from "common/molecules/editable-card"
import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { DeclareMonthlyQuantity } from "./declare-monthly-quantity"

export const MonthlyBiomethaneInjection = () => {
  const { t } = useTranslation()
  const portal = usePortal()

  const openDeclareMonthlyQuantityDialog = () => {
    portal((close) => <DeclareMonthlyQuantity onClose={close} data={[]} />)
  }

  return (
    <EditableCard
      title={t("Production mensuelle de biométhane injecté")}
      headerActions={
        <Button iconId="ri-add-line" onClick={openDeclareMonthlyQuantityDialog}>
          {t("Déclarer mes volumes mensuels")}
        </Button>
      }
    >
      {"Visualisez ou modifiez les volumes mensuels de biométhane injecté"}
    </EditableCard>
  )
}
