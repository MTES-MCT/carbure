import { useTranslation } from "react-i18next"
import { usePortal } from "common/components/portal"
import { Confirm } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration.provider"

export const usePageHeaderActions = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const notify = useNotify()
  const { currentAnnualDeclaration } = useAnnualDeclaration()
  const validateAnnualDeclarationMutation = useMutation(
    () => Promise.resolve(),
    {
      invalidates: ["annual-declaration"],
      onSuccess: () => {
        notify(t("Les informations ont bien été validées."), {
          variant: "success",
        })
      },
    }
  )

  const openValidateDeclarationDialog = () => {
    portal((close) => (
      <Confirm
        onClose={close}
        confirm={t("Valider")}
        onConfirm={validateAnnualDeclarationMutation.execute}
        title={t("Transmission de votre déclaration annuelle")}
        description={
          <>
            {t(
              "Votre déclaration (digestat et énergie) est complète, voulez-vous la transmettre à l'administration DGEC ?"
            )}
            <br />
            {currentAnnualDeclaration?.year &&
              t("Vous pourrez la corriger jusqu'au {{date}}", {
                date: `31/03/${currentAnnualDeclaration.year + 1}`,
              })}
          </>
        }
      />
    ))
  }

  const openCorrectionDeclarationDialog = () => {
    // TODO: Implémenter la logique de correction
  }

  return {
    openValidateDeclarationDialog,
    openCorrectionDeclarationDialog,
  }
}
