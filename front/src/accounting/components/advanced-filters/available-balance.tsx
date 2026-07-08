import { Notice } from "common/components/notice"

import { useUnit } from "common/hooks/unit"
import { useTranslation } from "react-i18next"
import { Icon } from "common/components/icon"
import { ExtendedUnitType } from "common/types"
import { formatAccountingUnit } from "accounting/utils/formatters"

export const AvailableBalance = ({
  loading,
  availableBalance,
  unit: _unit,
}: {
  loading: boolean
  availableBalance: number
  unit?: ExtendedUnitType
}) => {
  const { t } = useTranslation()
  const { unit } = useUnit(_unit)

  return (
    <Notice noColor variant={availableBalance <= 1 ? "warning" : "info"}>
      <div>
        {t("Solde disponible pour les filtres sélectionnés")}
        {" : "}
        {loading ? (
          <Icon name="ri-loader-line" size="md" />
        ) : (
          <b>{formatAccountingUnit(availableBalance, unit)}</b>
        )}
      </div>
    </Notice>
  )
}
