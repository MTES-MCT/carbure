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
  const { value, bind, setField } = useFormContext<GHGRangeFormProps>()
  const { ghgReductionMin, ghgReductionMax } = formatGhgReduction(
    balance?.ghg_reduction_min ?? 50,
    balance?.ghg_reduction_max ?? 100
  )
  const gesBoundMin = value.gesBoundMin ?? ghgReductionMin
  const gesBoundMax = value.gesBoundMax ?? ghgReductionMax

  // When the component is mounted, set the gesBoundMin and gesBoundMax in the form only if they are not already set
  useEffect(() => {
    if (value.gesBoundMin === undefined) {
      setField("gesBoundMin", ghgReductionMin)
    }
    if (value.gesBoundMax === undefined) {
      setField("gesBoundMax", ghgReductionMax)
    }
  }, [gesBoundMin, gesBoundMax, ghgReductionMin, ghgReductionMax])

  return (
    <DoubleRange
      step={0.01}
      suffix="%"
      label={t("Définissez le taux de réduction GES des lots à prélever")}
      animateOn={`${ghgReductionMin}-${ghgReductionMax}`}
      minRange={bind("gesBoundMin", {
        value: gesBoundMin,
        onChange: onRangeChange
          ? (_value) => onRangeChange(_value!, gesBoundMax)
          : undefined,
      })}
      maxRange={bind("gesBoundMax", {
        value: gesBoundMax,
        onChange: onRangeChange
          ? (_value) => onRangeChange(gesBoundMin, _value!)
          : undefined,
      })}
      min={ghgReductionMin}
      max={ghgReductionMax}
    />
  )
}
