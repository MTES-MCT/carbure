import css from "./progress-bar.module.css"
import cl from "clsx"
import { Text } from "common/components/text"
import { useLayoutEffect, useRef, useState } from "react"

export type ProgressBarProps = {
  // Target objective
  targetQuantity: number

  // Currently declared quantity
  declaredQuantity: number

  // Available quantity that can be added
  availableQuantity: number
}

const PROGRESS_BAR_STEPS = 5
const STEP_VALUE = 100 / (PROGRESS_BAR_STEPS - 1) // Don't count 0

const getHalfWidthElement = (element?: HTMLSpanElement) =>
  element && element.offsetWidth > 0 ? element.offsetWidth / 2 : 0

export const ProgressBar = ({
  targetQuantity,
  declaredQuantity,
  availableQuantity,
}: ProgressBarProps) => {
  const declaredValueRef = useRef<HTMLSpanElement>()
  const availableValueRef = useRef<HTMLSpanElement>()

  const [declaredValueWidth, setDeclaredValueWidth] = useState("")
  const [availableValueWidth, setAvailableValueWidth] = useState("")

  const declaredPercent = (declaredQuantity * 100) / targetQuantity
  const availablePercent =
    ((declaredQuantity + availableQuantity) * 100) / targetQuantity

  // Get the width of the text to center it with the progress bar
  useLayoutEffect(() => {
    setDeclaredValueWidth(
      `calc(${declaredPercent}% + ${getHalfWidthElement(declaredValueRef?.current)}px)`
    )
    setAvailableValueWidth(
      `calc(${availablePercent - declaredPercent}% + ${declaredPercent === 0 ? `${getHalfWidthElement(availableValueRef?.current)}px` : "0px"})`
    )
  }, [declaredPercent, availablePercent])

  return (
    <div>
      <div className={css["progress-bar__header"]}>
        {/* Only show declared percentage if value is greater than 0 */}
        {declaredQuantity > 0 ? (
          <span
            className={css["progress-bar__quantity-declared-value"]}
            style={{
              width: declaredValueWidth,
            }}
          >
            <Text size="xs" is="span" domRef={declaredValueRef}>
              {declaredPercent}%
            </Text>
          </span>
        ) : null}

        {/* Only show available percentage if available quantity is greater than declared quantity */}
        {availableQuantity > declaredQuantity && (
          <span
            className={css["progress-bar__quantity-available-value"]}
            style={{
              width: availableValueWidth,
            }}
          >
            <Text size="xs" is="span" domRef={availableValueRef}>
              {availablePercent}%
            </Text>
          </span>
        )}
      </div>
      <div className={css["progress-bar"]}>
        {declaredQuantity ? (
          <span
            className={css["progress-bar--quantity-declared"]}
            style={{ width: `${declaredPercent}%` }}
          />
        ) : null}
        {availableQuantity ? (
          <span
            className={css["progress-bar--quantity-available"]}
            style={{ width: `${availablePercent}%` }}
          />
        ) : null}
        {/*  Display points on the progress bar */}
        {Array.from(Array(PROGRESS_BAR_STEPS).keys()).map((index) => (
          <div
            key={`step-${index}`}
            className={cl(
              css["progress-bar__step"],
              STEP_VALUE * index <= availablePercent &&
                availablePercent > 0 &&
                css["progress-bar__step--filled"]
            )}
            style={{ left: `calc(${STEP_VALUE * index}% - 2px)` }}
          ></div>
        ))}
      </div>
      <div className={css["progress-bar__footer"]}>
        <Text size="xs" className={css["progress-bar__text"]}>
          0%
        </Text>
        <Text size="xs" className={css["progress-bar__text"]}>
          100%
        </Text>
      </div>
    </div>
  )
}
