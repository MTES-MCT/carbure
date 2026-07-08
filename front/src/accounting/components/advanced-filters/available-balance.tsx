import { Notice } from "common/components/notice"

import { useUnit } from "common/hooks/unit"
import { useTranslation } from "react-i18next"
import { Icon } from "common/components/icon"
import { ExtendedUnitType } from "common/types"
import { floorNumber } from "common/utils/formatters"

export const AvailableBalance = ({
  loading,
  availableBalance,
  unit,
}: {
  loading: boolean
  availableBalance: number
  unit?: ExtendedUnitType
}) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit(unit)

  const availableBalanceFormatted = floorNumber(availableBalance, 2)

  return (
    <Notice
      noColor
      variant={availableBalanceFormatted <= 1 ? "warning" : "info"}
    >
      <div>
        {t("Solde disponible pour les filtres sélectionnés")}
        {" : "}
        {loading ? (
          <Icon name="ri-loader-line" size="md" />
        ) : (
          <b>
            {formatUnit(availableBalance, {
              fractionDigits: 2,
              mode: "floor",
            })}
          </b>
        )}
      </div>
    </Notice>
  )
}
