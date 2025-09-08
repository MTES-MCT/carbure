import { useTranslation } from "react-i18next"
import { EditableCard } from "common/molecules/editable-card"
import { Button } from "common/components/button2"
import { DeclareMonthlyQuantity } from "./declare-monthly-quantity"
import HashRoute from "common/components/hash-route"

export const MonthlyBiomethaneInjection = () => {
  const { t } = useTranslation()

  return (
    <>
      <EditableCard
        title={t("Production mensuelle de biométhane injecté")}
        headerActions={
          <Button
            iconId="ri-add-line"
            linkProps={{
              to: { hash: "monthly-reports" },
            }}
          >
            {t("Déclarer mes volumes mensuels")}
          </Button>
        }
      >
        {"Visualisez ou modifiez les volumes mensuels de biométhane injecté"}
      </EditableCard>
      <HashRoute path="monthly-reports" element={<DeclareMonthlyQuantity />} />
    </>
  )
}
