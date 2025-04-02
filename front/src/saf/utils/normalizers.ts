import { Normalizer } from "common/utils/normalize"
import { ConsumptionType } from "saf/types"
import { formatConsumptionType } from "./formatters"
import i18next from "i18next"

export const normalizeConsumptionType: Normalizer<ConsumptionType> = (
  consumptionType
) => ({
  value: consumptionType,
  label: i18next.t(formatConsumptionType(consumptionType)),
})
