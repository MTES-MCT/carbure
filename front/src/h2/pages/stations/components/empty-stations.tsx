import { usePortal } from "common/components/portal"
import { EmptyState } from "common/molecules/empty-state"
import { useTranslation } from "react-i18next"
import { CreateStationDialog } from "./create-station-dialog/create-station-dialog"

export const EmptyStations = () => {
  const { t } = useTranslation()
  const portal = usePortal()

  return (
    <EmptyState
      title={t("Vous n’avez pas encore saisi de stations d’hydrogène")}
      description={t(
        "Veuillez saisir les informations de vos stations afin de pouvoir commencer à déclarer des lots d’hydrogène"
      )}
      buttonProps={{
        children: t("Inscrire une station"),
        iconId: "ri-add-line",
        onClick: () => {
          portal((onClose) => <CreateStationDialog onClose={onClose} />)
        },
      }}
    />
  )
}
