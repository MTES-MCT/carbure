import { Balance, ElecBalance } from "accounting/types"
import {
  formatAccountingNumber,
  formatSector,
} from "accounting/utils/formatters"
import { Column, Cell } from "common/components/table2"
import { CONVERSIONS } from "common/utils/formatters"
import { useTranslation } from "react-i18next"
import { SectorObjective } from "../../types"

const toGJ = (value: number) => CONVERSIONS.energy.MJ_TO_GJ(value)

// Format all values in the table to GJ
const formatValue = (value: number) => formatAccountingNumber(toGJ(value))

export const useBiofuelTeneurColumns = () => {
  const { t } = useTranslation()
  const columns: Column<Balance>[] = [
    {
      header: t("Biocarburant"),
      cell: (item) => item.biofuel?.code,
    },
    {
      header: t("Catégorie"),
      cell: (item) => item.customs_category,
    },
    {
      header: `${t("Solde initial")} (GJ)`,
      cell: (item) => (
        <Cell
          text={formatValue(item.available_balance + item.pending_teneur)}
        />
      ),
    },
    {
      header: `${t("Teneur à valider")} (GJ)`,
      cell: (item) => <Cell text={formatValue(item.pending_teneur)} />,
    },
    {
      header: `${t("Solde final")} (GJ)`,
      cell: (item) => <Cell text={formatValue(item.available_balance)} />,
    },
  ]

  return columns
}

// Data is retrieved from the sector objectives, so the unit is already in GJ
export const useBiofuelTeneurSectorColumns = () => {
  const { t } = useTranslation()
  const columns: Column<SectorObjective>[] = [
    {
      header: t("Filière"),
      cell: (item) => <Cell text={formatSector(item.code)} />,
    },
    {
      header: `${t("Avancement initial")} (GJ)`,
      cell: (item) => (
        <Cell text={formatAccountingNumber(item.teneur_declared)} />
      ),
    },
    {
      header: `${t("Teneur à valider")} (GJ)`,
      cell: (item) => (
        <Cell text={formatAccountingNumber(item.pending_teneur)} />
      ),
    },
    {
      header: `${t("Avancement final")} (GJ)`,
      cell: (item) => (
        <Cell
          text={formatAccountingNumber(
            item.teneur_declared + item.pending_teneur
          )}
        />
      ),
    },
  ]

  return columns
}

export const useElecTeneurColumns = () => {
  const { t } = useTranslation()
  const columns: Column<ElecBalance>[] = [
    {
      header: t("Filière"),
      cell: (item) => <Cell text={formatSector(item.sector)} />,
    },
    {
      header: `${t("Solde initial")} (GJ)`,
      cell: (item) => (
        <Cell
          text={formatValue(item.available_balance + item.pending_teneur)}
        />
      ),
    },
    {
      header: `${t("Teneur à valider")} (GJ)`,
      cell: (item) => <Cell text={formatValue(item.pending_teneur)} />,
    },
    {
      header: `${t("Solde final")} (GJ)`,
      cell: (item) => <Cell text={formatValue(item.available_balance)} />,
    },
  ]

  return columns
}
