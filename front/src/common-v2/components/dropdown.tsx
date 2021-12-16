import React, { useCallback, useEffect, useRef } from "react"
import cl from "clsx"
import Portal from "./portal"
import css from "./dropdown.module.css"
import useControlledState from "../hooks/controlled-state"

export interface Trigger {
  anchor?: Anchor
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
  anchor = Anchors.bottomLeft,
}: DropdownProps) => {
  const [open, _setOpen] = useControlledState(false, openControlled, onToggle)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const setOpen = useCallback(
    (willOpen) => {
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

    const box = trigger.getBoundingClientRect()
    Object.assign(dropdown.style, anchor(box))
    dropdown.style.minWidth = `${box.width}px`
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

    function onResize(e: Event) {
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

      if (!isInsideTrigger && !isInsideDropdown) {
        setOpen(false)
      }
    }

    function onBlur(e: FocusEvent) {
      if (!isInside(dropdownRef.current, e.relatedTarget)) {
        setOpen(false)
      }
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

    window.addEventListener("click", onClickOustide)
    trigger.addEventListener("click", onClick)
    trigger.addEventListener("keydown", onKeyDown, true)
    trigger.addEventListener("blur", onBlur, true)

    return () => {
      window.removeEventListener("click", onClickOustide)
      trigger.removeEventListener("click", onClick)
      trigger.removeEventListener("keydown", onKeyDown, true)
      trigger.removeEventListener("blur", onBlur, true)
    }
  }, [triggerRef, dropdownRef, open, setOpen])

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
  return (container as Element)?.contains(element as Element)
}

type CustomRenderer = (config: { close: () => void }) => React.ReactNode

export default Dropdown
