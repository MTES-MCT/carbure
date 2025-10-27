import React from "react"
import { useTranslation } from "react-i18next"
import { Confirm, ConfirmProps } from "common/components/dialog2"

export type AnnualDeclarationResetDialogProps = Pick<
  ConfirmProps,
  "onClose" | "onConfirm"
>

export const AnnualDeclarationResetDialog = ({
  onClose,
  onConfirm,
}: AnnualDeclarationResetDialogProps) => {
  const { t } = useTranslation()

  return (
    <Confirm
      onClose={onClose}
      onConfirm={onConfirm}
      title={t("Votre déclaration annuelle doit être soumise à nouveau")}
      confirm={t("J'ai compris")}
      description={
        <>
          <p>
            {t(
              "Vous avez modifié des champs de la section contrat ou production."
            )}
          </p>
          <p>
            {t(
              "Rendez-vous dans les sections digestat et énergie pour compléter les nouveaux champs et soumettre votre déclaration à nouveau."
            )}
          </p>
        </>
      }
      hideCancel
    />
  )
}
