import { useTranslation } from "react-i18next"
import { usePortal } from "common/components/portal"
import { Confirm } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration.provider"
import { validateAnnualDeclaration } from "biomethane/api"
import useEntity from "common/hooks/entity"
import { HttpError } from "common/services/api-fetch"

export const usePageHeaderActions = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const notify = useNotify()
  const entity = useEntity()
  const { currentAnnualDeclaration } = useAnnualDeclaration()
  const validateAnnualDeclarationMutation = useMutation(
    () => validateAnnualDeclaration(entity.id),
    {
      invalidates: ["current-annual-declaration"],
      onSuccess: () => {
        notify(t("Votre déclaration a bien été transmise."), {
          variant: "success",
        })
      },
      onError: (err) => {
        const errorCode = (err as HttpError).status
        if (errorCode === 400) {
          notify(
            t("Votre déclaration n'est pas complète, veuillez la compléter."),
            {
              variant: "danger",
            }
          )
        }
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
