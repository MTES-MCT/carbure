import { QuantityFormProps } from "./quantity-form.types"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"
import { OperationText } from "../operation-text"
import { formatNumber } from "common/utils/formatters"
import { DEFAULT_UNIT_OPERATION } from "accounting/config"

export const QuantitySummary = ({ values }: { values: QuantityFormProps }) => {
  const { t } = useTranslation()
  const { formatUnit } = useUnit(DEFAULT_UNIT_OPERATION)
  if (!values.quantity || !values.avoided_emissions) {
    return null
  }

  return (
    <>
      <OperationText
        title={t("Quantité")}
        description={formatUnit(values.quantity, {
          fractionDigits: 10,
        })}
      />
      <OperationText
        title={t("TCO2 évitées équivalentes")}
        description={formatNumber(values.avoided_emissions, {
          fractionDigits: 10,
        })}
      />
      <OperationText
        title={t("Nombre de lots prélevés")}
        description={values.selected_lots?.length ?? 0}
      />
    </>
  )
}
