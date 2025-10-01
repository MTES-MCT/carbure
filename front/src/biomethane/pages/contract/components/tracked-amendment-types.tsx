import { useMemo } from "react"
import { TrackedAmendmentTypes } from "../types"
import { Notice } from "common/components/notice"
import { useTranslation } from "react-i18next"

export const ErrorTrackedAmendmentTypes = ({
  trackedAmendmentTypes,
}: {
  trackedAmendmentTypes: TrackedAmendmentTypes[]
}) => {
  const { t } = useTranslation()
  const message = useMemo(() => {
    const map = {
      [TrackedAmendmentTypes.CMAX_PAP_UPDATE]: "Cmax/PAP",
      [TrackedAmendmentTypes.CMAX_ANNUALIZATION]: t("Cmax annualisée"),
      [TrackedAmendmentTypes.PRODUCER_BUYER_INFO_CHANGE]: t("Acheteur"),
    }
    return trackedAmendmentTypes.map((type) => map[type]).join(", ")
  }, [trackedAmendmentTypes, t])

  return (
    <Notice
      variant="warning"
      icon="ri-error-warning-line"
      title={
        <>
          {t(
            "Les champs suivants ont été modifié sur le contrat : {{message}}.",
            { message }
          )}
          {"  "}
          {t("Veuillez charger l'avenant correspondant aux modifications.")}
        </>
      }
    ></Notice>
  )
}
