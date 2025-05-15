import { Balance, ElecBalance } from "accounting/types"
import { formatSector } from "accounting/utils/formatters"
import { Column, Cell } from "common/components/table2"
import { CONVERSIONS, floorNumber, formatNumber } from "common/utils/formatters"
import { useTranslation } from "react-i18next"

const HeaderWithSup = ({ children }: { children: React.ReactNode }) => (
  <span>
    {children}
    <sup>*</sup>
  </span>
)

// Format all values in the table to GJ
const formatValue = (value: number) =>
  formatNumber(CONVERSIONS.energy.MJ_TO_GJ(value), {
    fractionDigits: 0,
  })

const floorValue = (value: number) =>
  floorNumber(CONVERSIONS.energy.MJ_TO_GJ(value), 0)

export const useBiofuelTeneurColumns = () => {
  const { t } = useTranslation()
  const columns: Column<Balance>[] = [
    {
      header: t("Filière"),
      cell: (item) => <Cell text={formatSector(item.sector)} />,
    },
    {
      header: t("Biocarburant"),
      cell: (item) => item.biofuel?.code,
    },
    {
      header: t("Catégorie"),
      cell: (item) => item.customs_category,
    },
    {
      header: <HeaderWithSup>{t("Solde initial")}</HeaderWithSup>,
      cell: (item) => (
        <Cell
          text={formatNumber(
            floorValue(item.available_balance + item.pending_teneur),
            {
              fractionDigits: 0,
            }
          )}
        />
      ),
    },
    {
      header: <HeaderWithSup>{t("Teneur à valider")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.pending_teneur)} />,
    },
    {
      header: <HeaderWithSup>{t("Solde final")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.available_balance)} />,
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
      header: <HeaderWithSup>{t("Solde initial")}</HeaderWithSup>,
      cell: (item) => (
        <Cell
          text={formatNumber(
            floorValue(item.available_balance) +
              floorValue(item.pending_teneur),
            {
              fractionDigits: 0,
            }
          )}
        />
      ),
    },
    {
      header: <HeaderWithSup>{t("Teneur à valider")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.pending_teneur)} />,
    },
    {
      header: <HeaderWithSup>{t("Solde final")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.available_balance)} />,
    },
  ]

  return columns
}
