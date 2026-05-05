import {
  Range as BaseRange,
  RangeProps as BaseRangeProps,
} from "@codegouvfr/react-dsfr/Range"
import { ComponentProps } from "react"
import css from "./double-range.module.css"
import cl from "clsx"
import { usePulseAnimation } from "./use-pulse-animation"

type BoundaryProps = Omit<ComponentProps<"input">, "value" | "onChange"> & {
  value?: number
  onChange?: (value: number) => void
}

export type DoubleRangeProps = Omit<BaseRangeProps, "double"> & {
  minRange?: BoundaryProps
  maxRange?: BoundaryProps
  animateOn?: unknown
}

export const DoubleRange = ({
  min,
  max,
  step,
  minRange,
  maxRange,
  animateOn,
  ...props
}: DoubleRangeProps) => {
  const animate = usePulseAnimation(animateOn, 300)

  return (
    <BaseRange
      {...props}
      className={cl(
        min === max && css["same-value"],
        animate && css["animate-values"],
        props.className
      )}
      double
      min={min}
      max={max}
      step={step}
      nativeInputProps={[
        {
          value: minRange?.value ?? min,
          onChange: (e) => {
            const value = Number.parseFloat(e.target.value)
            minRange?.onChange?.(value)
            if (value > (maxRange?.value ?? Infinity)) {
              maxRange?.onChange?.(value)
            }
          },
        },
        {
          value: maxRange?.value ?? max,
          onChange: (e) => {
            const value = Number.parseFloat(e.target.value)
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
