import css from "./progress-bar.module.css"
import cl from "clsx"
import { Text } from "common/components/text"
import { useRef } from "react"

export type ProgressBarProps = {
  // Objectif à atteindre
  quantityObjective: number

  quantityDeclared: number

  availableQuantity: number
}

const PROGRESS_BAR_STEPS = 5
const STEP_VALUE = 100 / (PROGRESS_BAR_STEPS - 1) // Don't count 0

const getHalfWidthElement = (element?: HTMLSpanElement) =>
  element && element.offsetWidth > 0 ? element.offsetWidth / 2 : 0

export const ProgressBar = ({
  quantityObjective,
  quantityDeclared,
  availableQuantity,
}: ProgressBarProps) => {
  const quantityDeclaredValueRef = useRef<HTMLSpanElement>()
  const quantityAvailableValueRef = useRef<HTMLSpanElement>()

  const quantityDeclaredPercent = (quantityDeclared * 100) / quantityObjective
  const availableQuantityPercent =
    ((quantityDeclared + availableQuantity) * 100) / quantityObjective

  // 14px est la moitié de la taille du texte (voir pour une ref)
  const quantityDeclaredValueWidth = `calc(${quantityDeclaredPercent}% + ${getHalfWidthElement(quantityDeclaredValueRef?.current)}px)`
  const quantityAvailableValueWidth = `calc(${availableQuantityPercent - quantityDeclaredPercent}% + ${quantityDeclaredPercent === 0 ? `${getHalfWidthElement(quantityAvailableValueRef?.current)}px` : "0px"})`

  return (
    <div>
      <div className={css["progress-bar__header"]}>
        {/* On affiche le pourcentage de quantité déclarée que si la valeur est supérieure à 0  */}
        {quantityDeclared > 0 ? (
          <span
            className={css["progress-bar__quantity-declared-value"]}
            style={{
              width: quantityDeclaredValueWidth,
            }}
          >
            <Text size="xs" is="span" ref={quantityDeclaredValueRef}>
              {quantityDeclaredPercent}%
            </Text>
          </span>
        ) : null}

        {/* On affiche le pourcentage que l'on peut atteindre avec la quantité dispo uniquement si la quantité dispo est supérieure à la quantité déclarée */}
        {availableQuantity > quantityDeclared && (
          <span
            className={css["progress-bar__quantity-available-value"]}
            style={{
              width: quantityAvailableValueWidth,
            }}
          >
            <Text size="xs" is="span" ref={quantityAvailableValueRef}>
              {availableQuantityPercent}%
            </Text>
          </span>
        )}
      </div>
      <div className={css["progress-bar"]}>
        {quantityDeclared ? (
          <span
            className={css["progress-bar--quantity-declared"]}
            style={{ width: `${quantityDeclaredPercent}%` }}
          />
        ) : null}
        {availableQuantity ? (
          <span
            className={css["progress-bar--quantity-available"]}
            style={{ width: `${availableQuantityPercent}%` }}
          />
        ) : null}
        {/*  Display points on the progress bar */}
        {Array.from(Array(PROGRESS_BAR_STEPS).keys()).map((index) => (
          <div
            key={`step-${index}`}
            className={cl(
              css["progress-bar__step"],
              STEP_VALUE * index <= availableQuantityPercent &&
                availableQuantityPercent > 0 &&
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
