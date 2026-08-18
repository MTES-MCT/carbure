import Select, { SelectProps } from "common/components/select"
import { useMemo } from "react"
import { useTranslation } from "react-i18next"

import {
  FUEL_USAGES,
  getFuelUsageNormalizer,
} from "transactions/constants/fuel-usage"
import { FuelUsage } from "transactions/types"

type FuelUsageSelectProps = Omit<
  SelectProps<FuelUsage>,
  "options" | "normalize"
>

export const FuelUsageSelect = ({
  label,
  placeholder,
  ...props
}: FuelUsageSelectProps) => {
  const { t } = useTranslation()
  const normalize = useMemo(() => getFuelUsageNormalizer(t), [t])

  return (
    <Select
      label={label ?? t("Usage du carburant")}
      placeholder={placeholder ?? t("Sélectionner un usage")}
      options={FUEL_USAGES}
      normalize={normalize}
      {...props}
    />
  )
}
