import { Column } from "common/components/table2"
import { compact } from "common/utils/collection"
import { BiomethaneDigestateStorage } from "../../types"
import { useTranslation } from "react-i18next"
import { formatNumber } from "common/utils/formatters"
import { Button } from "common/components/button2"
import { usePortal } from "common/components/portal"
import { useDeleteDigestateStorage } from "../../production.hooks"
import { Confirm } from "common/components/dialog2"
import { useSelectedEntity } from "common/providers/selected-entity-provider"

export const useDigestateStorageColumns = () => {
  const { t } = useTranslation()
  const portal = usePortal()
  const { execute: deleteStorage } = useDeleteDigestateStorage()
  const { hasSelectedEntity } = useSelectedEntity()

  const columns: Column<BiomethaneDigestateStorage>[] = compact([
    { header: t("Dispositif"), cell: (storage) => storage.type },
    {
      header: t("Capacité de stockage (m3)"),
      cell: (storage) => formatNumber(storage.capacity) || "-",
    },
    {
      header: t("Couverture du stockage"),
      cell: (storage) => (storage.has_cover ? t("Oui") : t("Non")),
    },
    {
      header: t("Récupération du biogaz"),
      cell: (storage) => (storage.has_biogas_recovery ? t("Oui") : t("Non")),
    },
    !hasSelectedEntity && {
      header: t("Actions"),
      cell: (storage) => (
        <Button
          iconId="fr-icon-delete-fill"
          size="small"
          priority="secondary"
          title={t("Supprimer")}
          onClick={() =>
            portal((close) => (
              <Confirm
                title={t("Supprimer le fichier")}
                description={t(
                  "Êtes-vous sûr de vouloir supprimer ce stockage de digestat ?"
                )}
                confirm={t("Supprimer")}
                customVariant="danger"
                onClose={close}
                onConfirm={async () => {
                  await deleteStorage(storage.id)
                  close()
                }}
              />
            ))
          }
        />
      ),
    },
  ])

  return columns
}
