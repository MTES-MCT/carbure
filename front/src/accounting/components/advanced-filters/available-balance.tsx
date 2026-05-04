import { Notice } from "common/components/notice"

import { useUnit } from "common/hooks/unit"
import { useTranslation } from "react-i18next"
import { Icon } from "common/components/icon"
import { Unit } from "common/types"

export const AvailableBalance = ({
  loading,
  availableBalance,
  unit,
}: {
  loading: boolean
  availableBalance: number
  unit?: Unit
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
            })}
          </b>
        )}
      </div>
    </Notice>
  )
}
