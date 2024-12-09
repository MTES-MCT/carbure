/**
 * This component is designed to be used when the container for
 * your elements is too small and you want to display a button
 * show more.
 */

import { ReactNode, useMemo, useRef } from "react"

type ShowMoreProps = {
  children: ReactNode
  text: string
}
export const ShowMore = ({ children, text }: ShowMoreProps) => {
  const containerRef = useRef()

  const visibleItems = useMemo(() => {
    if (!containerRef?.current?.children) return null

    const containerWidth = containerRef?.current?.offsetWidth ?? 0
    const childrenWidth = Array.from(containerRef?.current?.children).reduce(
      (total, child, index) => {
        const width = total.width + (child?.offsetWidth ?? 0)
        const overflow = containerWidth < width
        return {
          width: total.width + (child?.offsetWidth ?? 0),
          index: overflow ? index : -1,
        }
      },
      {
        width: 0,
        index: -1,
      }
    )
    console.log("childdd", childrenWidth)
    return childrenWidth
  }, [containerRef])

  return (
    <div
      ref={containerRef}
      style={{ display: "flex", gap: "8px", flexWrap: "wrap" }}
    >
      {children}
      {text}
      {visibleItems}
    </div>
  )
}
