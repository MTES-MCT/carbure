import React, { useMemo } from "react"
import { useTranslation } from "react-i18next"
import { Confirm, ConfirmProps } from "common/components/dialog2"
import { AnnualDeclarationStatus } from "biomethane/types"

export type AnnualDeclarationResetDialogProps = Pick<
  ConfirmProps,
  "onClose" | "onConfirm"
> & {
  annualDeclarationStatus?: AnnualDeclarationStatus
}

export const AnnualDeclarationResetDialog = ({
  onClose,
  onConfirm,
  annualDeclarationStatus,
}: AnnualDeclarationResetDialogProps) => {
  const { t } = useTranslation()

  const props = useMemo(() => {
    const defaultTexts = {
      title: t("Nouveaux champs à remplir"),
      description: (
        <>
          <p>
            {t(
              "Vous avez modifié des champs de la page contrat ou production."
            )}
          </p>
          <p>
            {t(
              "Rendez-vous dans les pages digestat et énergie pour compléter les nouveaux champs."
            )}
          </p>
        </>
      ),
    }
    if (annualDeclarationStatus === AnnualDeclarationStatus.DECLARED) {
      return {
        title: t("Votre déclaration annuelle doit être soumise à nouveau"),
        description: (
          <>
            <p>
              {t(
                "Vous avez modifié des champs de la page contrat ou production."
              )}
            </p>
            <p>
              {t(
                "Rendez-vous dans les pages digestat et énergie pour compléter les nouveaux champs et soumettre votre déclaration à nouveau."
              )}
            </p>
          </>
        ),
      }
    }
    return defaultTexts
  }, [annualDeclarationStatus, t])

  return (
    <Confirm
      {...props}
      onClose={onClose}
      onConfirm={onConfirm}
      confirm={t("J'ai compris")}
      hideCancel
      size="medium"
    />
  )
}
