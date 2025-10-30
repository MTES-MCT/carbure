import { Confirm } from "common/components/dialog2"
import { Col } from "common/components/scaffold"
import { useTranslation } from "react-i18next"

interface DeleteMeterDialogProps {
  chargePointId: number
  onClose: () => void
}

export const DeleteMeterDialog = ({
  chargePointId,
  onClose,
}: DeleteMeterDialogProps) => {
  const { t } = useTranslation()

  async function onConfirmDelete() {
    console.log(chargePointId)
  }

  return (
    <Confirm
      customVariant="danger"
      title={t("Supprimer le compteur MID")}
      description={
        <Col style={{ gap: "var(--spacing-m)" }}>
          <p>{t("Souhaitez-vous effacer complètement ce compteur MID ?")}</p>
          <p>
            {t(
              "Cette opération est censée être réalisée uniquement lorsque le compteur a été ajouté par erreur au PDC."
            )}
          </p>
          <p>
            {t(
              "Si vous souhaitez seulement remplacer le compteur par un nouveau modèle, merci d'utiliser l'option 'Mon compteur MID a changé ?'"
            )}
          </p>
        </Col>
      }
      confirm={t("Supprimer")}
      onConfirm={onConfirmDelete}
      onClose={onClose}
    />
  )
}
