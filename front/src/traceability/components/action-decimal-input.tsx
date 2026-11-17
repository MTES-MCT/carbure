import { DecimalInput, DecimalInputProps } from "common/components/inputs2"
import { getStepFromFractionDigits } from "common/utils/formatters"

const ACTION_DECIMAL_STEP = getStepFromFractionDigits(3)

export const ActionDecimalInput = (props: DecimalInputProps) => (
  <DecimalInput step={ACTION_DECIMAL_STEP} {...props} />
)
