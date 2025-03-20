import css from "./progress-bar.module.css"
import cl from "clsx"
import { Text } from "common/components/text"
import { formatNumber, roundNumber } from "common/utils/formatters"
import { useLayoutEffect, useRef, useState } from "react"

export type ProgressBarProps = {
  // Target objective
  targetQuantity: number

  baseQuantity: number

  // Currently declared quantity
  declaredQuantity: number
}

const PROGRESS_BAR_STEPS = 5
const STEP_VALUE = 100 / (PROGRESS_BAR_STEPS - 1) // Don't count 0

const getTextPercentWidth = (element?: HTMLSpanElement) => {
  if (!element) return 0

  return element.offsetWidth / 2
}

export const ProgressBar = ({
  targetQuantity,
  baseQuantity,
  declaredQuantity,
}: ProgressBarProps) => {
  const basePercent = Number(
    roundNumber((baseQuantity * 100) / targetQuantity, 1)
  )

  const declaredPercent = Number(
    roundNumber(
      (Math.min(baseQuantity + declaredQuantity, targetQuantity) * 100) /
        targetQuantity,
      1
    )
  )

  const baseValueRef = useRef<HTMLSpanElement>()
  const declaredValueRef = useRef<HTMLSpanElement>()

  const [baseValueWidth, setBaseValueWidth] = useState<string | number>(0)
  const [declaredValueWidth, setDeclaredValueWidth] = useState<string | number>(
    0
  )

  useLayoutEffect(() => {
    const baseValueWidth = baseValueRef?.current?.offsetWidth ?? 0
    const declaredValueWidth = declaredValueRef?.current?.offsetWidth ?? 0
    setBaseValueWidth(`-${baseValueWidth / 2}px`)

    if (declaredPercent - basePercent < 10) {
      setDeclaredValueWidth(`-${baseValueWidth + 10}px`)
    } else {
      setDeclaredValueWidth(`-${declaredValueWidth / 2}px`)
    }
  }, [baseValueRef, declaredValueRef, declaredPercent, basePercent])

  return (
    <div className={css["progress-bar__container"]}>
      <div className={css["progress-bar"]}>
        {/* Only show declared percentage if value is greater than 0 */}
        {baseQuantity && baseQuantity > 0 ? (
          <span
            className={css["progress-bar--quantity-declared"]}
            style={{ width: `${basePercent}%` }}
          >
            <Text
              size="xs"
              is="span"
              className={css["progress-bar__quantity-declared-value"]}
              style={{ right: baseValueWidth }}
              domRef={baseValueRef}
            >
              {basePercent}%
            </Text>
          </span>
        ) : null}
        {/* Only show available percentage if available quantity is greater than declared quantity */}
        {declaredQuantity && declaredQuantity > baseQuantity ? (
          <span
            className={css["progress-bar--quantity-available"]}
            style={{ width: `${declaredPercent}%` }}
          >
            <Text
              size="xs"
              is="span"
              className={css["progress-bar__quantity-available-value"]}
              style={{ right: declaredValueWidth }}
              domRef={declaredValueRef}
            >
              {declaredPercent}%
            </Text>
          </span>
        ) : null}
        <div className={css["progress-bar__steps"]}>
          {/*  Display points on the progress bar */}
          {Array.from(Array(PROGRESS_BAR_STEPS).keys()).map((index) => (
            <div
              key={`step-${index}`}
              className={cl(
                css["progress-bar__step"],
                STEP_VALUE * index <= declaredPercent &&
                  declaredPercent > 0 &&
                  css["progress-bar__step--filled"]
              )}
              style={{ left: `calc(${STEP_VALUE * index}% - 2px)` }}
            ></div>
          ))}
        </div>
        <Text size="xs" className={css["progress-bar__zero-percent"]} is="span">
          0%
        </Text>
        <Text size="xs" className={css["progress-bar__100-percent"]} is="span">
          100%
        </Text>
      </div>
    </div>
  )
}
