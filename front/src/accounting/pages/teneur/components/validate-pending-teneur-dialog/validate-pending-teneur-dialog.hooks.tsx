import { formatSector } from "accounting/utils/formatters"
import { Column, Cell } from "common/components/table2"
import { apiTypes } from "common/services/api-fetch.types"
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

export const useValidatePendingTeneurDialog = () => {
  const { t } = useTranslation()
  const columns: Column<apiTypes["BalanceBySector"]>[] = [
    {
      header: t("Filière"),
      cell: (item) => <Cell text={formatSector(item.sector)} />,
    },
    {
      header: <HeaderWithSup>{t("Solde disponible")}</HeaderWithSup>,
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
      header: <HeaderWithSup>{t("Teneur déclarée")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.pending_teneur)} />,
    },
    {
      header: <HeaderWithSup>{t("Solde final")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.available_balance)} />,
    },
  ]

  return columns
}
