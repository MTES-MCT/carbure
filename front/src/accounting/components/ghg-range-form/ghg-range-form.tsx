import { Balance } from "accounting/types"
import { useFormContext } from "common/components/form2"

import { useTranslation } from "react-i18next"
import { GHGRangeFormProps } from "./ghg-range-form.types"
import { ceilNumber, floorNumber } from "common/utils/formatters"
import { DoubleRange } from "common/components/inputs2"
import { useEffect } from "react"

export const formatGhgReduction = (
  ghg_reduction_min: number,
  ghg_reduction_max: number
) => {
  if (ghg_reduction_min === ghg_reduction_max) {
    return {
      ghgReductionMin: ghg_reduction_min,
      ghgReductionMax: ghg_reduction_max,
    }
  }
  return {
    ghgReductionMin: floorNumber(ghg_reduction_min, 2),
    ghgReductionMax: ceilNumber(ghg_reduction_max, 2),
  }
}

type GHGRangeFormComponentProps = {
  balance: Balance
  onRangeChange?: (gesBoundMin: number, gesBoundMax: number) => void
}

export const GHGRangeForm = ({
  balance,
  onRangeChange,
}: GHGRangeFormComponentProps) => {
  const { t } = useTranslation()
  const { value, bind, setValue } = useFormContext<GHGRangeFormProps>()
  const { ghgReductionMin, ghgReductionMax } = formatGhgReduction(
    balance?.ghg_reduction_min ?? 50,
    balance?.ghg_reduction_max ?? 100
  )

  // When the component is mounted, init form values with the balance values only if they are not already set
  useEffect(() => {
    const formValue = {
      ...value,
      availableBalance: value.availableBalance ?? balance.available_balance,
      gesBoundMin: value.gesBoundMin ?? ghgReductionMin,
      gesBoundMax: value.gesBoundMax ?? ghgReductionMax,
    }

    setValue(formValue)
  }, [])

  return (
    <DoubleRange
      step={0.01}
      suffix="%"
      label={t("Définissez le taux de réduction GES des lots à prélever")}
      minRange={bind("gesBoundMin", {
        onChange: onRangeChange
          ? (_value) => onRangeChange(_value!, value.gesBoundMax!)
          : undefined,
      })}
      maxRange={bind("gesBoundMax", {
        onChange: onRangeChange
          ? (_value) => onRangeChange(value.gesBoundMin!, _value!)
          : undefined,
      })}
      min={ghgReductionMin}
      max={ghgReductionMax}
    />
  )
}
