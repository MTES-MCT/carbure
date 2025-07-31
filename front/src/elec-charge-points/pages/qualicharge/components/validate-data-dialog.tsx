import { Confirm, ConfirmProps } from "common/components/dialog2"
import { useTranslation } from "react-i18next"

export type ValidateDataDialogProps = {
  volume: number
  onConfirm: ConfirmProps["onConfirm"]
  onClose: ConfirmProps["onClose"]
}

export const ValidateDataDialog = ({
  volume,
  onConfirm,
  onClose,
}: ValidateDataDialogProps) => {
  const { t } = useTranslation()

  return (
    <Confirm
      title={t("Confirmer votre action")}
      description={
        <>
          <p>
            {t(
              "Êtes-vous sûr de valider l’ensemble des données Qualicharge sélectionnées ?"
            )}
          </p>
          <p>
            {t(
              "Votre compte sera crédité de certificats ENR à hauteur de {{volume}} MWH, une fois la validation DGEC effectuée.",
              {
                volume,
              }
            )}
          </p>
        </>
      }
      confirm={t("Valider")}
      icon="ri-check-line"
      variant="primary"
      onConfirm={onConfirm}
      onClose={onClose}
      hideCancel={false}
    />
  )
}
