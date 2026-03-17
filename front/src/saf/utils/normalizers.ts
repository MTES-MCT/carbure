import { Normalizer } from "common/utils/normalize"
import { ConsumptionType, EtsStatus } from "saf/types"
import { formatConsumptionType, formatEtsStatus } from "./formatters"
import i18next from "i18next"

export const normalizeConsumptionType: Normalizer<ConsumptionType> = (
  consumptionType
) => ({
  value: consumptionType,
  label: i18next.t(formatConsumptionType(consumptionType)),
})

export const normalizeEtsStatus: Normalizer<EtsStatus> = (etsStatus) => ({
  value: etsStatus,
  label: i18next.t(formatEtsStatus(etsStatus)),
})
