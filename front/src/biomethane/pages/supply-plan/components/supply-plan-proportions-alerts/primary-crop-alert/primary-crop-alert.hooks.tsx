import { useMemo } from "react"
import { useTranslation } from "react-i18next"

import { formatPercentage } from "common/utils/formatters"
import { TariffCoefficientProportions } from "../../../types"
import { getPrimaryCropAlertSeverity } from "./primary-crop-alert.utils"

type UsePrimaryCropAlertParams = {
  loading: boolean
  proportions?: TariffCoefficientProportions
}

export const usePrimaryCropAlert = ({
  loading,
  proportions,
}: UsePrimaryCropAlertParams) => {
  const { t } = useTranslation()

  const primaryCropPercent = proportions?.primary_crop ?? 0

  const description = useMemo(() => {
    if (loading) {
      return t("Chargement des proportions…")
    }

    if (!proportions) {
      return null
    }

    return t("Pourcentage de cultures principales = {{value}}", {
      value: formatPercentage(primaryCropPercent),
    })
  }, [loading, proportions, primaryCropPercent, t])

  const severity = useMemo(() => {
    if (loading || !proportions) {
      return "info" as const
    }
    return getPrimaryCropAlertSeverity(primaryCropPercent)
  }, [loading, proportions, primaryCropPercent])

  return {
    description,
    severity,
  }
}
