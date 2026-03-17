import { useTranslation } from "react-i18next"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { Button } from "common/components/button2"
import { DeclareMonthlyQuantity } from "./declare-monthly-quantity"
import HashRoute from "common/components/hash-route"
import { BiomethaneEnergy } from "../../types"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { Notice } from "common/components/notice"
import { useMemo } from "react"

export const MonthlyBiomethaneInjection = ({
  energy,
}: {
  energy?: BiomethaneEnergy
}) => {
  const { t } = useTranslation()
  const { canEditDeclaration } = useAnnualDeclaration()

  const messages = useMemo(() => {
    if (canEditDeclaration) {
      return {
        submit: t("Déclarer mes volumes mensuels"),
        view: t(
          "Déclarez ou modifiez les volumes mensuels de biométhane injecté"
        ),
      }
    }

    return {
      submit: t("Visualiser mes volumes mensuels"),
      view: t("Visualisez les volumes mensuels de biométhane injecté"),
    }
  }, [canEditDeclaration, t])

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
              {messages.submit}
            </Button>
          )
        }
      >
        {energy?.monthly_reports?.length === 0 ? (
          <Notice variant="warning" icon="ri-error-warning-line">
            {t("Aucun volume mensuel de biométhane injecté déclaré")}
          </Notice>
        ) : (
          messages.view
        )}
      </ManagedEditableCard>
      <HashRoute
        path="monthly-reports"
        element={
          <DeclareMonthlyQuantity
            isReadOnly={!canEditDeclaration}
            monthlyReports={energy?.monthly_reports ?? []}
          />
        }
      />
    </>
  )
}
