import { formatSector } from "accounting/utils/formatters"
import { Column, Cell } from "common/components/table2"
import { useUnit } from "common/hooks/unit"
import { apiTypes } from "common/services/api-fetch.types"
import { ExtendedUnit } from "common/types"
import { CONVERSIONS, formatNumber } from "common/utils/formatters"
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
    fractionDigits: 1,
  })

export const useValidatePendingTeneurDialog = () => {
  const { t } = useTranslation()
  const { unit } = useUnit(ExtendedUnit.GJ)
  const columns: Column<apiTypes["BalanceBySector"]>[] = [
    {
      header: t("Filière"),
      cell: (item) => <Cell text={t(formatSector(item.sector))} />,
    },
    {
      header: (
        <HeaderWithSup>{`${t("Solde initial")} (${unit.toLocaleUpperCase()})`}</HeaderWithSup>
      ),
      cell: (item) => (
        <Cell
          text={formatValue(
            item.initial_balance < 1 ? 0 : item.initial_balance
          )}
        />
      ),
    },
    {
      header: <HeaderWithSup>{t("Entrées")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.quantity.credit)} />,
    },
    {
      header: <HeaderWithSup>{t("Sorties")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.quantity.debit)} />,
    },
    {
      header: <HeaderWithSup>{t("Solde disponible")}</HeaderWithSup>,
      cell: (item) => (
        <Cell
          text={formatValue(item.available_balance - item.declared_teneur)}
        />
      ),
    },
    {
      header: <HeaderWithSup>{t("Teneur déclarée")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.declared_teneur)} />,
    },
    {
      header: <HeaderWithSup>{t("Solde final")}</HeaderWithSup>,
      cell: (item) => <Cell text={formatValue(item.available_balance)} />,
    },
  ]

  return columns
}
