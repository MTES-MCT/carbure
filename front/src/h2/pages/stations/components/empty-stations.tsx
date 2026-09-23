import { EmptyState } from "common/molecules/empty-state"
import { useH2Permissions } from "h2/hooks/use-h2-permissions"
import { useTranslation } from "react-i18next"
import { useCreateStationDialog } from "./create-station-dialog"

export const EmptyStations = () => {
  const { t } = useTranslation()
  const { canWriteStations } = useH2Permissions()
  const openCreateStationDialog = useCreateStationDialog()

  if (!canWriteStations) {
    return (
      <EmptyState
        title={t("Aucune station d’hydrogène")}
        description={t("Les sociétés HRS n’ont pas encore déclaré de station.")}
      />
    )
  }

  return (
    <EmptyState
      title={t("Vous n’avez pas encore saisi de stations d’hydrogène")}
      description={t(
        "Veuillez saisir les informations de vos stations afin de pouvoir commencer à déclarer des lots d’hydrogène"
      )}
      buttonProps={{
        children: t("Inscrire une station"),
        iconId: "ri-add-line",
        onClick: openCreateStationDialog,
      }}
    />
  )
}
