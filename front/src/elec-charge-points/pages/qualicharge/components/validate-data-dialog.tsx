import { Confirm, ConfirmProps } from "common/components/dialog2"
import useEntity from "common/hooks/entity"
import { formatNumber } from "common/utils/formatters"
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
  const entity = useEntity()
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
          {entity.isCPO && (
            <p>
              {t(
                "Votre compte sera crédité de certificats ENR à hauteur de {{volume}} MWH, une fois la validation DGEC effectuée.",
                {
                  volume: formatNumber(volume),
                }
              )}
            </p>
          )}
        </>
      }
      confirm={t("Valider")}
      icon="ri-check-line"
      variant="primary"
      onConfirm={onConfirm}
      onClose={onClose}
      hideCancel
    />
  )
}
