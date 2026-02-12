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
  patchAnnualDeclaration,
  validateAnnualDeclaration,
} from "biomethane/api"
import useEntity from "common/hooks/entity"
import { HttpError } from "common/services/api-fetch"
import { MissingFields } from "biomethane/components/missing-fields"
import { Text } from "common/components/text"
import { useNavigateToMissingFields } from "biomethane/components/missing-fields"
import { AnnualDeclarationStatus } from "biomethane/types"
import { DeclarationValidatedModalStep1 } from "./declaration-validated-modal/declaration-validated-modal-step1"

export const usePageHeaderActions = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const notify = useNotify()
  const entity = useEntity()
  const annualDeclarationData = useAnnualDeclaration()
  const { navigateToMissingFields } = useNavigateToMissingFields()

  const { annualDeclaration, annualDeclarationKey, selectedYear } =
    annualDeclarationData

  const validateAnnualDeclarationMutation = useMutation(
    () => validateAnnualDeclaration(entity.id, selectedYear),
    {
      invalidates: [annualDeclarationKey],
      onSuccess: () => {
        notify(t("Votre déclaration a bien été transmise."), {
          variant: "success",
        })
        portal((close) => <DeclarationValidatedModalStep1 onClose={close} />)
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
    () =>
      patchAnnualDeclaration(entity.id, selectedYear, {
        status: AnnualDeclarationStatus.IN_PROGRESS,
      }),
    {
      invalidates: [annualDeclarationKey],
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
              "Votre déclaration est complète, voulez-vous la transmettre à l'administration DGEC ?"
            )}
            <br />
            {annualDeclaration?.status ===
              AnnualDeclarationStatus.IN_PROGRESS && (
              <>
                {annualDeclaration?.year &&
                  t("Vous pourrez la corriger jusqu'au {{date}}", {
                    date: `31/03/${annualDeclaration.year + 1}`,
                  })}
              </>
            )}
            {annualDeclaration?.status === AnnualDeclarationStatus.OVERDUE &&
              t(
                "Attention, vous ne pourrez pas corriger votre déclaration une fois celle-ci transmise."
              )}
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
