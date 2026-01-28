import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"
import { Button } from "common/components/button2"
import { useTranslation } from "react-i18next"
import { useToggleDeclaration } from "./toggle-declaration-button.hooks"
import { useCreateDeclaration } from "../../hooks/use-create-declaration"
import { useCallback } from "react"

export const ToggleDeclarationButton = () => {
  const { t } = useTranslation()
  const { annualDeclaration } = useAnnualDeclaration()
  const toggleDeclaration = useToggleDeclaration()
  const createDeclaration = useCreateDeclaration()

  const handleToggleDeclaration = useCallback(() => {
    // If the declaration for the current biomethane producer and year is not found, create it
    if (annualDeclaration === undefined) {
      createDeclaration.execute()
    } else {
      // Otherwise, change the declaration open status
      toggleDeclaration.execute(annualDeclaration.is_open ?? false)
    }
  }, [annualDeclaration, toggleDeclaration, createDeclaration])

  return (
    <Button
      onClick={handleToggleDeclaration}
      loading={toggleDeclaration.loading}
      priority="secondary"
      asideX
    >
      {annualDeclaration?.is_open
        ? t("Fermer la déclaration")
        : t("Ouvrir la déclaration")}
    </Button>
  )
}
