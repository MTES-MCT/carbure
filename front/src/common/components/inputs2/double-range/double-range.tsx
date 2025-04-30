import {
  Range as BaseRange,
  RangeProps as BaseRangeProps,
} from "@codegouvfr/react-dsfr/Range"
import { ComponentProps } from "react"

type BoundaryProps = Omit<ComponentProps<"input">, "value" | "onChange"> & {
  value?: number
  onChange?: (value: number) => void
}

export type DoubleRangeProps = BaseRangeProps & {
  minRange?: BoundaryProps
  maxRange?: BoundaryProps
}

export const DoubleRange = ({
  min,
  max,
  step,
  minRange,
  maxRange,
  ...props
}: DoubleRangeProps) => {
  return (
    <BaseRange
      {...props}
      double
      min={min}
      max={max}
      step={step}
      nativeInputProps={[
        {
          ...minRange,
          value: minRange?.value ?? min,
          onChange: (e) => {
            const value = parseFloat(e.target.value)
            minRange?.onChange?.(value)
            if (value > (maxRange?.value ?? Infinity)) {
              maxRange?.onChange?.(value)
            }
          },
        },
        {
          ...maxRange,
          value: maxRange?.value ?? max,
          onChange: (e) => {
            const value = parseFloat(e.target.value)
            maxRange?.onChange?.(value)
            if (value < (minRange?.value ?? -Infinity)) {
              minRange?.onChange?.(value)
            }
          },
        },
      ]}
    />
  )
}
