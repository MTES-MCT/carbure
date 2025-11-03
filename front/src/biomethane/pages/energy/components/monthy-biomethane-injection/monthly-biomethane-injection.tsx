import { useTranslation } from "react-i18next"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { Button } from "common/components/button2"
import { DeclareMonthlyQuantity } from "./declare-monthly-quantity"
import HashRoute from "common/components/hash-route"
import { BiomethaneEnergy } from "../../types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export const MonthlyBiomethaneInjection = ({
  energy,
}: {
  energy?: BiomethaneEnergy
}) => {
  const { t } = useTranslation()
  const { canEditDeclaration } = useAnnualDeclaration()
  return (
    <>
      <ManagedEditableCard
        sectionId="monthly-biomethane-injection"
        title={t("Production mensuelle de biométhane injecté")}
        headerActions={
          !energy ? (
            <Button iconId="ri-add-line" disabled>
              {t("Déclarer mes volumes mensuels")}
            </Button>
          ) : (
            <Button
              iconId="ri-add-line"
              linkProps={{
                to: { hash: "monthly-reports" },
              }}
            >
              {!canEditDeclaration
                ? t("Visualiser mes volumes mensuels")
                : t("Déclarer mes volumes mensuels")}
            </Button>
          )
        }
      >
        {!canEditDeclaration
          ? t("Visualisez les volumes mensuels de biométhane injecté")
          : t(
              "Déclarez ou modifiez les volumes mensuels de biométhane injecté"
            )}
      </ManagedEditableCard>
      <HashRoute
        path="monthly-reports"
        element={<DeclareMonthlyQuantity isReadOnly={!canEditDeclaration} />}
      />
    </>
  )
}
