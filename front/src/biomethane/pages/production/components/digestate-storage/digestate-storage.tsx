import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { usePortal } from "common/components/portal"
import { Table } from "common/components/table2"
import { EditableCard } from "common/molecules/editable-card"
import { AddDigestateStorage } from "./add-digestate-storage"
import { useDigestateStorages } from "../../production.hooks"
import { useSelectedEntity } from "common/providers/selected-entity-provider"
import { useDigestateStorageColumns } from "./digestate-storage.hooks"

export function DigestateStorage() {
  const { t } = useTranslation()
  const { result: storages } = useDigestateStorages()
  const columns = useDigestateStorageColumns()
  const { hasSelectedEntity } = useSelectedEntity()

  const portal = usePortal()

  const totalCapacity =
    storages?.reduce((sum, storage) => sum + storage.capacity, 0) || 0

  return (
    <EditableCard
      title={t("Stockage de digestat")}
      headerActions={
        !hasSelectedEntity && (
          <Button
            iconId="ri-add-line"
            onClick={() =>
              portal((close) => <AddDigestateStorage onClose={close} />)
            }
          >
            {t("Ajouter un type de stockage")}
          </Button>
        )
      }
    >
      {Boolean(storages?.length) && (
        <Table rows={storages!} columns={columns} />
      )}

      <Notice>
        {t("Capacité totale de stockage")} : {totalCapacity} m3
      </Notice>
    </EditableCard>
  )
}
