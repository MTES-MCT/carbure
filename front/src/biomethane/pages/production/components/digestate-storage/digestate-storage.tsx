import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { usePortal } from "common/components/portal"
import { Table } from "common/components/table2"
import { EditableCard } from "common/molecules/editable-card"
import { Confirm } from "common/components/dialog2"
import { AddDigestateStorage } from "./add-digestate-storage"
import {
  useDigestateStorages,
  useDeleteDigestateStorage,
} from "../../production.hooks"
import { formatNumber } from "common/utils/formatters"

export function DigestateStorage() {
  const { t } = useTranslation()
  const { result: storages } = useDigestateStorages()
  const { execute: deleteStorage } = useDeleteDigestateStorage()

  const portal = usePortal()

  const totalCapacity =
    storages?.reduce((sum, storage) => sum + storage.capacity, 0) || 0

  return (
    <EditableCard
      title={t("Stockage de digestat")}
      headerActions={
        <Button
          iconId="ri-add-line"
          onClick={() =>
            portal((close) => <AddDigestateStorage onClose={close} />)
          }
        >
          {t("Ajouter un type de stockage")}
        </Button>
      }
    >
      {Boolean(storages?.length) && (
        <Table
          rows={storages!}
          columns={[
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
              cell: (storage) =>
                storage.has_biogas_recovery ? t("Oui") : t("Non"),
            },
            {
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
          ]}
        />
      )}

      <Notice>
        {t("Capacité totale de stockage")} : {totalCapacity} m3
      </Notice>
    </EditableCard>
  )
}
