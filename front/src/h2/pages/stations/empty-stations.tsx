import { EmptyState } from "common/molecules/empty-state"
import { useTranslation } from "react-i18next"

export const EmptyStations = () => {
  const { t } = useTranslation()

  return (
    <EmptyState
      title={t("Vous n’avez pas encore saisi de stations d’hydrogène")}
      description={t(
        "Veuillez saisir les informations de vos stations afin de pouvoir commencer à déclarer des lots d’hydrogène"
      )}
      buttonProps={{
        children: t("Inscrire une station"),
        iconId: "ri-add-line",
      }}
    />
  )
}
