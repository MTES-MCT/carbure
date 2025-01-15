import React, { useCallback, useEffect, useRef } from "react"
import cl from "clsx"
import Portal from "./portal"
import css from "./dropdown.module.css"
import useControlledState from "../hooks/controlled-state"

export interface Trigger {
  anchor?: string
  onOpen?: () => void
  onClose?: () => void
  onToggle?: (open: boolean) => void
}

export interface DropdownProps extends Trigger {
  triggerRef: React.RefObject<HTMLElement>
  open?: boolean
  children: React.ReactNode | CustomRenderer
  className?: string
  style?: React.CSSProperties
  openOnHover?: boolean
}

export const Dropdown = ({
  triggerRef,
  open: openControlled,
  className,
  style,
  children,
  onOpen,
  onClose,
  onToggle,
  anchor = "bottom start",
  openOnHover = false,
}: DropdownProps) => {
  const [open, _setOpen] = useControlledState(false, openControlled, onToggle)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const isHoverTimeout = useRef<NodeJS.Timeout>()
  const setOpen = useCallback(
    (willOpen: boolean) => {
      if (willOpen !== open) {
        _setOpen(willOpen)
        if (willOpen) onOpen?.()
        else onClose?.()
      }
    },
    [open, onOpen, onClose, _setOpen]
  )

  // position the dropdown relative to the target
  useEffect(() => {
    const dropdown = dropdownRef.current
    const trigger = triggerRef.current
    if (!dropdown || !trigger) return

    const triggerBox = trigger.getBoundingClientRect()
    const dropdownBox = dropdown.getBoundingClientRect()

    const position = computeAnchoredPosition(triggerBox, dropdownBox, anchor)
    // Object.assign(dropdown.style, position)
    dropdown!.style.transform = `translate3d(${position.left}px, ${position.top}px, 0)`
    dropdown.style.minWidth = `${triggerBox.width}px`
  })

  // automatically close the dropdown if a scroll is detected
  useEffect(() => {
    if (!open) return

    function onScroll(e: Event) {
      // close only if we're not scrolling inside the dropdown
      if (!isInside(dropdownRef.current, e.target)) {
        setOpen(false)
      }
    }

    window.addEventListener("scroll", onScroll, true)
    return () => window.removeEventListener("scroll", onScroll, true)
  }, [triggerRef, open, setOpen])

  // automatically close the dropdown if window is resized
  useEffect(() => {
    if (!open) return

    function onResize() {
      setOpen(false)
    }

    window.addEventListener("resize", onResize, true)
    return () => window.removeEventListener("resize", onResize, true)
  }, [open, setOpen])

  // watch for interactions on the target to act as trigger
  useEffect(() => {
    const trigger = triggerRef.current
    if (trigger === null) return

    function onClick(e: MouseEvent) {
      const isCaptive = (e.target as Element).closest("[data-captive]") !== null

      if (!isCaptive) {
        setOpen(!open)
      }
    }

    function onClickOustide(e: MouseEvent) {
      if (!open) return

      const isInsideTrigger = isInside(triggerRef.current, e.target)
      const isInsideDropdown = isInside(dropdownRef.current, e.target)
      console.log("click outside legacy", {
        t: e.target,
        triggerRef: triggerRef.current,
        dropdownRef: dropdownRef.current,
        isInsideTrigger,
        isInsideDropdown,
      })
      if (!isInsideTrigger && !isInsideDropdown) {
        setOpen(false)
      }
    }

    function onBlur(e: FocusEvent) {
      if (!isInside(dropdownRef.current, e.relatedTarget)) {
        setOpen(false)
      }
    }

    function onHover(e: MouseEvent) {
      if (open) return
      if (!isInside(dropdownRef.current, e.relatedTarget)) {
        isHoverTimeout.current = setTimeout(() => {
          setOpen(true)
        }, 150)
      }
    }

    function onHoverOut() {
      if (isHoverTimeout.current) clearTimeout(isHoverTimeout.current)
      if (open) setOpen(false)
    }

    function onKeyDown(e: KeyboardEvent) {
      switch (e.key) {
        // toggle dropdown when typing Space
        case "Space":
          setOpen(!open)
          break

        // open dropdown when using up/down arrows
        case "ArrowUp":
        case "ArrowDown":
          e.preventDefault()
          setOpen(true)
          break
      }
    }

    if (openOnHover) {
      trigger.addEventListener("mouseover", onHover)
      trigger.addEventListener("mouseout", onHoverOut)
    }

    window.addEventListener("click", onClickOustide)
    trigger.addEventListener("click", onClick)
    trigger.addEventListener("keydown", onKeyDown, true)
    trigger.addEventListener("blur", onBlur, true)

    return () => {
      window.removeEventListener("click", onClickOustide)

      if (openOnHover) {
        trigger.removeEventListener("mouseover", onHover)
        trigger.removeEventListener("mouseout", onHoverOut)
      }

      trigger.removeEventListener("click", onClick)
      trigger.removeEventListener("keydown", onKeyDown, true)
      trigger.removeEventListener("blur", onBlur, true)

      if (isHoverTimeout.current) clearTimeout(isHoverTimeout.current)
    }
  }, [triggerRef, dropdownRef, open, setOpen, openOnHover])

  function onFocus() {
    setOpen(true)
  }

  function onBlur(e: React.FocusEvent) {
    const isInsideTrigger = isInside(triggerRef.current, e.relatedTarget)
    const isInsideDropdown = isInside(dropdownRef.current, e.relatedTarget)

    if (!isInsideTrigger && !isInsideDropdown) {
      setOpen(false)
    }
  }

  if (!open) return null

  return (
    <Portal onClose={() => setOpen(false)}>
      <div
        ref={dropdownRef}
        data-dropdown
        tabIndex={0}
        className={cl(css.dropdown, className)}
        style={{ ...style, position: "fixed" }}
        onFocus={onFocus}
        onBlur={onBlur}
      >
        {typeof children === "function"
          ? children({ close: () => setOpen(false) })
          : children}
      </div>
    </Portal>
  )
}

export interface Position {
  top?: string
  right?: string
  bottom?: string
  left?: string
}

export type Anchor = (box: DOMRect) => Position

export const Anchors = {
  bottomLeft: (box: DOMRect): Position => ({
    top: box.top + box.height + "px",
    left: box.left + "px",
  }),
  bottomRight: (box: DOMRect): Position => ({
    top: box.top + box.height + "px",
    right: window.innerWidth - box.right + "px",
  }),
  topLeft: (box: DOMRect): Position => ({
    bottom: window.innerHeight - box.top + "px",
    left: box.left + "px",
  }),
}

export function isInside(
  container: EventTarget | Element | null,
  element: EventTarget | Element | null
) {
  console.log("isInside2", {
    container,
    element,
    isInside: (container as Element)?.contains(element as Element),
  })
  return (container as Element)?.contains(element as Element)
}

type CustomRenderer = (config: { close: () => void }) => React.ReactNode

export function computeAnchoredPosition(
  target: DOMRect,
  sticky: DOMRect,
  anchor: string
): { top: number; left: number } {
  let top = 0
  let left = 0

  const [side, align] = anchor.split(" ")

  // top and bottom anchors
  if (side === "top" || side === "bottom") {
    const vertical = {
      top: target.top - sticky.height,
      bottom: target.bottom,
      start: target.left,
      center: target.left + target.width / 2 - sticky.width / 2,
      end: target.right - sticky.width,
    }

    if (side === "top") {
      top = vertical.top
    } else if (side === "bottom") {
      top = vertical.bottom
    }

    if (align === "start") {
      left = vertical.start
    } else if (align === "end") {
      left = vertical.end
    } else if (align === "center" || align === undefined) {
      left = vertical.center
    }

    // try to fit overlay position to screen borders
    if (top + sticky.height > window.innerHeight) top = vertical.top
    if (top < 0) top = vertical.bottom
    if (left + sticky.width > window.innerWidth) left = vertical.end
    if (left < 0) left = vertical.start
  }
  // left and right anchors
  else if (side === "left" || side === "right") {
    const horizontal = {
      left: target.left - sticky.width,
      right: target.right,
      start: target.top,
      center: target.top + target.height / 2 - sticky.height / 2,
      end: target.bottom - sticky.height,
    }

    if (side === "left") {
      left = horizontal.left
    } else if (side === "right") {
      left = horizontal.right
    }

    if (align === "start") {
      top = horizontal.start
    } else if (align === "end") {
      top = horizontal.end
    } else if (align === "center" || align === undefined) {
      top = horizontal.center
    }

    // try to fit overlay position to screen borders
    if (left + sticky.width > window.innerWidth) left = horizontal.left
    if (left < 0) left = horizontal.right
    if (top + sticky.height > window.innerHeight) top = horizontal.end
    if (top < 0) top = horizontal.start
  }

  return { top, left }
}

export default Dropdown
