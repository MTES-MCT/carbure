import { useTranslation } from "react-i18next"
import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { usePortal } from "common/components/portal"
import { Table } from "common/components/table2"
import { AddDigestateStorage } from "./add-digestate-storage"
import { useDigestateStorages } from "../../production.hooks"
import { useAllowedToEdit } from "biomethane/hooks/use-allowed-to-edit"
import { useDigestateStorageColumns } from "./digestate-storage.hooks"
import { ManagedEditableCard } from "common/molecules/editable-card/managed-editable-card"
import { useAnnualDeclaration } from "biomethane/providers/annual-declaration"

export function DigestateStorage() {
  const { t } = useTranslation()
  const { result: storages } = useDigestateStorages()
  const columns = useDigestateStorageColumns()
  const allowedToEdit = useAllowedToEdit()
  const { annualDeclarationKey } = useAnnualDeclaration()

  const portal = usePortal()

  const totalCapacity =
    storages?.reduce((sum, storage) => sum + storage.capacity, 0) || 0

  return (
    <ManagedEditableCard
      sectionId="digestate-storage"
      title={t("Stockage de digestat")}
      readOnly={!allowedToEdit}
      headerActions={
        allowedToEdit && (
          <Button
            iconId="ri-add-line"
            onClick={() =>
              portal((close) => (
                <AddDigestateStorage
                  onClose={close}
                  annualDeclarationKey={annualDeclarationKey}
                />
              ))
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

      {storages?.length === 0 ? (
        <Notice variant="warning" icon="ri-error-warning-line">
          {t("Aucun type de stockage déclaré")}
        </Notice>
      ) : (
        <Notice>
          {t("Capacité totale de stockage")} : {totalCapacity} m3
        </Notice>
      )}
    </ManagedEditableCard>
  )
}
