/**
 * This component is designed to be used when the container for
 * your elements is too small and you want to display a button
 * show more.
 */

import { ReactNode, useCallback, useEffect, useRef, useState } from "react"
import styles from "./show-more.module.css"
import { Button } from "../button2"
import cl from "clsx"

type ShowMoreProps = {
  children: ReactNode[]
  text: string
}
export const ShowMore = ({
  children,
  text = "voir plus de filtres",
}: ShowMoreProps) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const hiddenElementsRef = useRef<HTMLDivElement>(null)
  const showMoreButtonRef = useRef<HTMLButtonElement>(null)
  const [visibleItems, _setVisibleItems] = useState<ReactNode[]>(children)
  const [isVisible, setIsVisible] = useState(false)

  const getFirstOverflowIndex = useCallback(() => {
    if (
      !containerRef?.current ||
      !hiddenElementsRef?.current?.children ||
      !showMoreButtonRef?.current
    )
      return -1

    const containerWidth = containerRef?.current?.offsetWidth ?? 0
    const showMoreButtonWidth = showMoreButtonRef?.current?.offsetWidth ?? 0

    let totalWidth = showMoreButtonWidth
    const firstOverflowIndex = Array.from(
      hiddenElementsRef?.current?.children
    ).findIndex((child) => {
      const width = (child as HTMLElement)?.offsetWidth ?? 0
      const overflow = containerWidth < totalWidth + width + 8
      console.log({
        containerWidth,
        showMoreButtonWidth,
        totalWidth,
        width,
        overflow,
      })
      totalWidth += width + 8
      return overflow
    })

    return firstOverflowIndex
  }, [containerRef, hiddenElementsRef])

  const setVisibleItems = useCallback(() => {
    console.log("SET VISIBLE ITEMS")
    const firstOverflowIndex = getFirstOverflowIndex()

    _setVisibleItems(
      firstOverflowIndex === -1
        ? children
        : children.slice(0, firstOverflowIndex - 1)
    )
  }, [getFirstOverflowIndex, _setVisibleItems, children])

  useEffect(() => {
    if (containerRef.current) {
      console.log("USE EFFECT")
      setVisibleItems()
    }
  }, [])

  useEffect(() => {
    window.addEventListener("resize", setVisibleItems)
    return () => {
      window.removeEventListener("resize", setVisibleItems)
    }
  }, [setVisibleItems])

  return (
    <div ref={containerRef} className={styles["show-more-container"]}>
      <div
        ref={hiddenElementsRef}
        className={styles["show-more-hidden-items"]}
        style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}
      >
        {children}
        <Button
          ref={showMoreButtonRef}
          priority="tertiary no outline"
          customPriority="link"
        >
          {text}
        </Button>
      </div>
      <div
        className={cl(styles["visible-items"], isVisible && styles["visible"])}
      >
        {visibleItems}
        {visibleItems.length !== children.length && (
          <Button
            customPriority="link"
            onClick={() => {
              _setVisibleItems(children)
              setIsVisible(true)
            }}
            className={styles["show-more-button"]}
          >
            {text}
          </Button>
        )}
      </div>
    </div>
  )
}
