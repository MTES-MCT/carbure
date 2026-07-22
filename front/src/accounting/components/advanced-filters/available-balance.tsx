import { Notice } from "common/components/notice"

import { useUnit } from "common/hooks/unit"
import { useTranslation } from "react-i18next"
import { Icon } from "common/components/icon"
import { formatAccountingUnit } from "accounting/utils/formatters"
import { DEFAULT_UNIT_OPERATION } from "accounting/config"

export const AvailableBalance = ({
  loading,
  availableBalance,
}: {
  loading: boolean
  availableBalance: number
}) => {
  const { t } = useTranslation()
  const { unit } = useUnit(DEFAULT_UNIT_OPERATION)

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
