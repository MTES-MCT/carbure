import { Badge } from "@codegouvfr/react-dsfr/Badge"
import { useTranslation } from "react-i18next"

export const VolumeAvailabilityBadge = () => {
  const { t } = useTranslation()

  return <Badge severity="success">{t("Disponible")}</Badge>
}
