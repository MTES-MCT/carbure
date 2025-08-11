import { Button } from "common/components/button2"
import { Notice } from "common/components/notice"
import { usePortal } from "common/components/portal"
import { Table } from "common/components/table2"
import { EditableCard } from "common/molecules/editable-card"
import { useTranslation } from "react-i18next"
import { AddDigestateStorage } from "./add-digestate-storage"

export function DigestateStorage() {
  const { t } = useTranslation()

  const portal = usePortal()

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
      <Table
        rows={[{}]}
        columns={[
          { header: t("Dispositif"), cell: () => "-" },
          { header: t("Capacité de stockage (m3)"), cell: () => "-" },
          { header: t("Couverture du stockage"), cell: () => "-" },
          { header: t("Récupération du biogaz"), cell: () => "-" },
        ]}
      />

      <Notice>
        {t("Capacité totale de stockage")} : {0} m3
      </Notice>
    </EditableCard>
  )
}
