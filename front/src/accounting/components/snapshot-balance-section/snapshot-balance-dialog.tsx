import { useTranslation } from "react-i18next"
import Dialog from "common/components/dialog2/dialog"
import { Notice } from "common/components/notice"
import { Portal } from "common/components/portal"
import { Table } from "common/components/table2"
import { apiTypes } from "common/services/api-fetch.types"
import { formatNumber, formatUnit } from "common/utils/formatters"
import { formatSector } from "accounting/utils/formatters"
import css from "./snapshot-balance-section.module.css"
import { ExtendedUnit } from "common/types"

type BalanceEntry = apiTypes["SnapshotBalanceEntry"]

export const SnapshotBalanceDialog = ({
  title,
  entries,
  onClose,
}: {
  title: string
  entries: BalanceEntry[]
  onClose: () => void
}) => {
  const { t } = useTranslation()
  const columns = [
    {
      header: t("Filière"),
      cell: (row: BalanceEntry) => formatSector(row.sector),
    },
    {
      header: t("Biocarburant"),
      cell: (row: BalanceEntry) => row.biofuel ?? "-",
    },
    {
      header: t("Catégorie"),
      cell: (row: BalanceEntry) => row.customs_category ?? "-",
    },
    {
      header: t("Quantité (L/GJ)"),
      cell: (row: BalanceEntry) => (
        <>
          {formatNumber(row.volume)} L
          <br />
          <span style={{ color: "var(--text-mention-grey)" }}>
            {formatUnit(row.energy / 1000, ExtendedUnit.GJ)}
          </span>
        </>
      ),
    },
    {
      header: t("tCO2 évitées"),
      cell: (row: BalanceEntry) => formatNumber(row.saved_emissions),
    },
  ]

  return (
    <Portal>
      <Dialog
        fullWidth
        onClose={onClose}
        header={<Dialog.Title>{title}</Dialog.Title>}
      >
        {entries.length === 0 && (
          <Notice noColor variant="info">
            {t("Aucun solde disponible pour cette année.")}
          </Notice>
        )}
        <div className={css.tableContainer}>
          {entries.length > 0 && (
            <Table className={css.table} columns={columns} rows={entries} />
          )}
        </div>
      </Dialog>
    </Portal>
  )
}
