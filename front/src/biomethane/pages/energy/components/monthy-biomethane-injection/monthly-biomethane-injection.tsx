import { useTranslation } from "react-i18next"
import { EditableCard } from "common/molecules/editable-card"
import { Button } from "common/components/button2"

export const MonthlyBiomethaneInjection = () => {
  const { t } = useTranslation()

  return (
    <EditableCard
      title={t("Production mensuelle de biométhane injecté")}
      headerActions={
        <Button iconId="ri-add-line">
          {t("Déclarer mes volumes mensuels")}
        </Button>
      }
    >
      {() => <div>MonthlyBiomethaneInjection</div>}
    </EditableCard>
  )
}
