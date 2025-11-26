import { Confirm } from "common/components/dialog2"
import { Col } from "common/components/scaffold"
import { useTranslation } from "react-i18next"
import { deleteMeter } from "./api"
import useEntity from "common/hooks/entity"
import { useNotify } from "common/components/notifications"
import { useMutation } from "common/hooks/async"
import { AxiosError } from "axios"

interface DeleteMeterDialogProps {
  chargePointId: number
  onClose: () => void
}

export const DeleteMeterDialog = ({
  chargePointId,
  onClose,
}: DeleteMeterDialogProps) => {
  const { t } = useTranslation()

  const notify = useNotify()
  const entity = useEntity()
  const deletion = useMutation(deleteMeter, {
    invalidates: ["charge-points-details"],
    onSuccess: () => {
      onClose()
      notify(t("Le compteur a bien été supprimé."), {
        variant: "success",
      })
    },
    onError: (e) => {
      const error = (e as AxiosError<{ error: string }>).response?.data.error

      if (error === "READINGS_ALREADY_REGISTERED") {
        notify(
          t(
            "Impossible de supprimer le compteur, des relevés y sont déjà associés. Veuillez contacter l'administration."
          ),
          { variant: "danger" }
        )
      } else {
        notify(
          t("Une erreur est survenue lors de la suppression du compteur."),
          { variant: "danger" }
        )
      }
    },
  })

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
      onConfirm={() => deletion.execute(entity.id, chargePointId)}
      onClose={onClose}
    />
  )
}
