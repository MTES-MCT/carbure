import React from "react"
import { useTranslation } from "react-i18next"
import { Confirm, ConfirmProps } from "common/components/dialog2"

export type AnnualDeclarationConfirmDialogProps = Pick<
  ConfirmProps,
  "onClose" | "onConfirm"
>

export const AnnualDeclarationConfirmDialog = ({
  onClose,
  onConfirm,
}: AnnualDeclarationConfirmDialogProps) => {
  const { t } = useTranslation()

  return (
    <Confirm
      onClose={onClose}
      onConfirm={onConfirm}
      title={t("Votre déclaration annuelle doit être soumise à nouveau")}
      confirm={t("Confirmer")}
      description={
        <>
          <p>
            {t(
              "Vous allez modifier des champs de la section contrat ou production."
            )}
          </p>
          <p>
            {t(
              "Après la sauvegarde de ces changements, rendez-vous dans les sections digestat et énergie pour compléter les nouveaux champs et soumettre votre déclaration à nous."
            )}
          </p>
        </>
      }
    />
  )
}
