import React, { useLayoutEffect, useState } from "react"
import ReactDOM from "react-dom"
import { DOMProps } from "./types"

const Overlay = (props: DOMProps<HTMLDivElement>) => {
  const [container, setContainer] = useState<HTMLDivElement | null>(null)

  useLayoutEffect(() => {
    const div = document.createElement("div")
    document.body.appendChild(div)
    setContainer(div)
    return () => div.remove()
  }, [])

  if (!container) return null

  return ReactDOM.createPortal(<div {...props} />, container)
}

interface Position {
  top?: number
  right?: number
  bottom?: number
  left?: number
}

export const Anchors = {
  bottomLeft: (box: DOMRect): Position => ({
    top: box.top + box.height,
    left: box.left,
  }),
}

export type RelativeOverlayProps = DOMProps<
  HTMLDivElement,
  {
    at: React.RefObject<Element>
    anchor?: (box: DOMRect) => Position
  }
>

export function RelativeOverlay({
  at,
  children,
  anchor: computePosition = Anchors.bottomLeft,
  ...props
}: RelativeOverlayProps) {
  const [position, setPosition] = useState<Position>({})

  useLayoutEffect(() => {
    function updatePosition() {
      if (!at.current) return

      const box = at.current.getBoundingClientRect()
      const computed = computePosition(box)

      setPosition(computed)
    }

    updatePosition()
    window.addEventListener("scroll", updatePosition, true)
    return () => window.removeEventListener("scroll", updatePosition, true)
  }, [at, computePosition])

  if (Object.keys(position).length === 0) return null

  return (
    <Overlay
      {...props}
      style={{ ...props.style, position: "fixed", ...position }}
    >
      {children}
    </Overlay>
  )
}

export default Overlay
