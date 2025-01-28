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
  children: ReactNode
  showMoreText?: string
  showLessText?: string
}

export const ShowMore = ({
  children,
  showMoreText = "Voir plus de filtres",
  showLessText = "Voir moins",
}: ShowMoreProps) => {
  if (!Array.isArray(children)) {
    throw new Error("Children must be a list of elements to work")
  }

  const containerRef = useRef<HTMLDivElement>(null)
  const hiddenElementsRef = useRef<HTMLDivElement>(null)
  const showMoreButtonRef = useRef<HTMLButtonElement>(null)
  const [visibleItems, _setVisibleItems] = useState<ReactNode[]>(children)
  const [isVisible, setIsVisible] = useState(false)

  // Return the index of the first overflow item to slice the children array
  const getFirstOverflowIndex = useCallback(() => {
    if (
      !containerRef?.current ||
      !hiddenElementsRef?.current?.children ||
      !showMoreButtonRef?.current
    )
      return -1

    const containerWidth = containerRef?.current?.offsetWidth ?? 0
    const showMoreButtonWidth = showMoreButtonRef?.current?.offsetWidth ?? 0

    const findOverflow = (defaultWidth = 0) => {
      if (!hiddenElementsRef?.current?.children) return -1

      let totalWidth = defaultWidth

      // Check how many items can be displayed in the container
      const firstOverflowIndex = Array.from(
        hiddenElementsRef?.current?.children
      ).findIndex((child, index) => {
        const width = (child as HTMLElement)?.offsetWidth ?? 0

        // add gap only if it's not the last item
        const widthWithGap =
          index !== hiddenElementsRef?.current?.children.length
            ? width + 8
            : width

        const overflow = containerWidth < totalWidth + widthWithGap
        totalWidth += widthWithGap
        return overflow
      })

      return firstOverflowIndex
    }

    const firstOverflowIndex = findOverflow()

    // If only some items can be displayed, recalculate how many items can be displayed with the button show more
    if (firstOverflowIndex !== -1) {
      return findOverflow(showMoreButtonWidth)
    }

    return firstOverflowIndex
  }, [containerRef, hiddenElementsRef])

  const setVisibleItems = useCallback(() => {
    const firstOverflowIndex = getFirstOverflowIndex()

    if (firstOverflowIndex !== -1) {
      _setVisibleItems(children.slice(0, firstOverflowIndex))
    }
  }, [getFirstOverflowIndex, _setVisibleItems, children])

  useEffect(() => {
    if (
      !containerRef.current ||
      !hiddenElementsRef.current ||
      !showMoreButtonRef.current
    )
      return

    const resizeObserver = new ResizeObserver(() => {
      setVisibleItems()
    })

    // Define a observer on the hidden element div to trigger the setVisibleItems function when the size of the hidden element div changes
    resizeObserver.observe(hiddenElementsRef.current)
    resizeObserver.observe(showMoreButtonRef.current)

    return () => {
      resizeObserver.disconnect()
    }
  }, [setVisibleItems])

  return (
    <div ref={containerRef} className={styles["show-more-container"]}>
      <div
        className={styles["show-more-hidden-items"]}
        style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}
      >
        <div
          style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}
          ref={hiddenElementsRef}
        >
          {children}
        </div>
        <Button
          ref={showMoreButtonRef}
          priority="tertiary no outline"
          customPriority="link"
          nativeButtonProps={{ role: "none" }}
          className={styles["show-more-button"]}
        >
          {showMoreText}
        </Button>
      </div>
      <div
        className={cl(styles["visible-items"], isVisible && styles["visible"])}
      >
        {visibleItems.length !== children.length && !isVisible
          ? visibleItems
          : children}
        {visibleItems.length !== children.length && (
          <Button
            customPriority="link"
            onClick={() => {
              setIsVisible(!isVisible)
            }}
            className={styles["show-more-button"]}
          >
            {isVisible ? showLessText : showMoreText}
          </Button>
        )}
      </div>
    </div>
  )
}
