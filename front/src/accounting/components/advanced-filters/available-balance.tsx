import { Notice } from "common/components/notice"

import { useUnit } from "common/hooks/unit"
import { useTranslation } from "react-i18next"
import { Icon } from "common/components/icon"
import { ExtendedUnitType } from "common/types"

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

  return (
    <Notice noColor variant="info">
      <div>
        {t("Solde disponible pour les filtres sélectionnés")}
        {" : "}
        {loading ? (
          <Icon name="ri-loader-line" size="md" />
        ) : (
          <b>
            {formatUnit(availableBalance, {
              fractionDigits: 0,
              mode: "floor",
            })}
          </b>
        )}
      </div>
    </Notice>
  )
}
