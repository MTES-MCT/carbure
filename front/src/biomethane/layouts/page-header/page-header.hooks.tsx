import { useTranslation } from "react-i18next"
import { usePortal } from "common/components/portal"
import { Confirm } from "common/components/dialog2"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import {
  AnnualDeclarationContext,
  useAnnualDeclaration,
} from "biomethane/providers/annual-declaration"
import {
  correctAnnualDeclaration,
  validateAnnualDeclaration,
} from "biomethane/api"
import useEntity from "common/hooks/entity"
import { HttpError } from "common/services/api-fetch"
import { MissingFields } from "biomethane/components/missing-fields"
import { Text } from "common/components/text"
import { useNavigateToMissingFields } from "biomethane/components/missing-fields"

export const usePageHeaderActions = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const notify = useNotify()
  const entity = useEntity()
  const annualDeclarationData = useAnnualDeclaration()
  const { navigateToMissingFields } = useNavigateToMissingFields()

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
  const correctAnnualDeclarationMutation = useMutation(
    () => correctAnnualDeclaration(entity.id),
    {
      invalidates: ["current-annual-declaration"],
      onSuccess: () => {
        notify(
          t(
            "Votre déclaration est repassée à en cours, vous pouvez la corriger."
          ),
          {
            variant: "success",
          }
        )
      },
      onError: () => {
        notify(
          t(
            "Une erreur est survenue lors de la correction de votre déclaration."
          ),
          {
            variant: "danger",
          }
        )
      },
    }
  )

  const { currentAnnualDeclaration } = annualDeclarationData

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
  const openMissingFieldsDialog = () => {
    portal((close) => (
      <Confirm
        onClose={close}
        confirm={t("Corriger")}
        onConfirm={() => {
          close()
          navigateToMissingFields()
          return Promise.resolve()
        }}
        title={t("Erreurs sur votre déclaration annuelle")}
        size="medium"
        description={
          <>
            <AnnualDeclarationContext.Provider value={annualDeclarationData}>
              <MissingFields onPageClick={close} />
            </AnnualDeclarationContext.Provider>
            <Text>
              {t(
                "Veuillez remplir ces champs et soumettre votre déclaration à nouveau."
              )}
            </Text>
          </>
        }
        hideCancel
      />
    ))
  }

  return {
    openValidateDeclarationDialog,
    openMissingFieldsDialog,
    correctAnnualDeclarationMutation,
  }
}
