import { Notice } from "common/components/notice"

import { useUnit } from "common/hooks/unit"
import { useTranslation } from "react-i18next"
import { Icon } from "common/components/icon"

export const AvailableBalance = ({
  loading,
  availableBalance,
}: {
  loading: boolean
  availableBalance: number
}) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit()

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
