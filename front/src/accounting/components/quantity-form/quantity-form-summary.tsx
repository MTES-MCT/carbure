import { QuantityFormProps } from "./quantity-form.types"
import { useTranslation } from "react-i18next"
import { useUnit } from "common/hooks/unit"
import { OperationText } from "../operation-text"
import { DEFAULT_UNIT_OPERATION } from "accounting/config"
import {
  formatAccountingUnit,
  formatTCO2Number,
} from "accounting/utils/formatters"

export const QuantitySummary = ({ values }: { values: QuantityFormProps }) => {
  const { t } = useTranslation()
  const { unit } = useUnit(DEFAULT_UNIT_OPERATION)
  if (!values.quantity || !values.avoided_emissions) {
    return null
  }

  return (
    <>
      <OperationText
        title={t("Quantité")}
        description={formatAccountingUnit(values.quantity, unit)}
      />
      <OperationText
        title={t("TCO2 évitées équivalentes")}
        description={formatTCO2Number(values.avoided_emissions)}
      />
      <OperationText
        title={t("Nombre de lots prélevés")}
        description={values.selected_lots?.length ?? 0}
      />
    </>
  )
}
