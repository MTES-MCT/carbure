import React, { useEffect, useRef, useState } from "react"
import ReactDOM from "react-dom"
import cl from "clsx"

import styles from "./dropdown.module.css"

import { SystemProps } from "."
import { ChevronDown } from "./icons"

const portal = document.getElementById("dropdown")!

// scroll to the specific dropdown option when the focus changes
function scrollToIndex(list: Element | null, focused: number) {
  if (list && list.children[focused]) {
    list.children[focused].scrollIntoView({
      block: "nearest",
      inline: "nearest",
    })
  }
}

// get the absolute position of the option list on screen based on the current position of the target
function getPosition(
  target: Element,
  above?: boolean,
  end?: boolean
): React.CSSProperties {
  const bbox = target.getBoundingClientRect()
  const position: React.CSSProperties = { minWidth: bbox.width }

  if (above) {
    position.bottom = window.innerHeight - bbox.top
  } else {
    position.top = bbox.top + bbox.height
  }

  if (end) {
    position.right = window.innerWidth - bbox.right
  } else {
    position.left = bbox.left
  }

  return position
}

// control focus with the arrow keys, validate change with Enter
function useKeyboardControls<T>(
  list: Element | null,
  focused: number,
  options: T[],
  setFocus: (i: number) => void,
  onChange: (e: T) => void,
  onFocus?: (e: T) => void
) {
  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      // move up
      if (e.key === "ArrowUp") {
        e.preventDefault()

        const prev = Math.max(0, focused - 1)
        onFocus && onFocus(options[prev])
        scrollToIndex(list, prev)
        setFocus(prev)
      }
      // move down
      else if (e.key === "ArrowDown") {
        e.preventDefault()

        const next = Math.min(focused + 1, options.length - 1)
        onFocus && onFocus(options[next])
        scrollToIndex(list, next)
        setFocus(next)
      }
      // select focused option
      else if (e.key === "Enter") {
        e.preventDefault()
        onChange(options[focused])
      }
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [options, list, focused, onFocus, onChange, setFocus])
}

// dumb polling to reposition the options in case of scrolling
function useAdjustPosition(
  parent: Element,
  setPosition: (p: React.CSSProperties) => void,
  above?: boolean,
  end?: boolean
) {
  useEffect(() => {
    const interval = setInterval(
      () => setPosition(getPosition(parent, above, end)),
      100
    )
    return () => clearInterval(interval)
  }, [setPosition, parent, above, end])
}

function isInside(container?: Element | null, element?: EventTarget | null) {
  return (
    element &&
    container &&
    element instanceof Element &&
    container.contains(element)
  )
}

export function useDropdown(target?: Element | null) {
  const [isOpen, setOpen] = useState(false)

  function toggle(value?: any) {
    if (typeof value === "boolean") {
      setOpen(value)
    } else {
      setOpen(!isOpen)
    }
  }

  // close dropdown when clicking outside
  useEffect(() => {
    if (!isOpen) return

    function onCloseClick(e: MouseEvent) {
      if (!isInside(target, e.target)) {
        setOpen(false)
      }
    }

    function onCloseKey(e: KeyboardEvent) {
      if (["Escape", "Tab"].includes(e.key)) {
        // prevent this event from triggering other similar callbacks
        // like the one that closes open modals
        e.stopImmediatePropagation()
        setOpen(false)
      }
    }

    window.addEventListener("click", onCloseClick)
    window.addEventListener("keydown", onCloseKey)

    return () => {
      window.removeEventListener("click", onCloseClick)
      window.removeEventListener("keydown", onCloseKey)
    }
  }, [isOpen, target])

  return { isOpen, toggle }
}

type DropdownLabelProps = SystemProps &
  React.HTMLProps<HTMLDivElement> & {
    onEnter?: () => void
    onLeave?: () => void
  }

export const DropdownLabel = ({
  children,
  className,
  onEnter,
  onLeave,
  ...props
}: DropdownLabelProps) => {
  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter" && onEnter) {
      onEnter()
    }
  }

  return (
    <div
      {...props}
      tabIndex={0}
      className={cl(styles.dropdownLabel, className)}
      onKeyDown={onKeyDown}
      onBlur={onLeave}
    >
      {children}
      <ChevronDown className={styles.dropdownArrow} />
    </div>
  )
}

type DropdownItemProps = React.HTMLProps<HTMLLIElement> & {
  selected?: boolean
  focused?: boolean
  className?: string
  allowFocus?: boolean
  children: React.ReactNode
}

export const DropdownItem = ({
  selected,
  focused,
  className,
  children,
  allowFocus,
  ...props
}: DropdownItemProps) => (
  <li
    {...props}
    onMouseDown={allowFocus ? undefined : (e) => e.preventDefault()}
    className={cl(
      className,
      styles.dropdownItem,
      selected && styles.selectedOption,
      focused && styles.focusedOption
    )}
  >
    {children}
  </li>
)

type DropdownProps = {
  above?: boolean
  end?: boolean
  parent: Element
  className?: string
  children: React.ReactNode
  listRef?: React.RefObject<HTMLUListElement>
  onMouseDown?: (e: React.MouseEvent) => void
}

export function Dropdown({
  above,
  end,
  parent,
  className,
  children,
  listRef,
  onMouseDown,
}: DropdownProps) {
  const [position, setPosition] = useState<React.CSSProperties | null>(null)

  useAdjustPosition(parent, setPosition, above, end)

  if (position === null) {
    setPosition(getPosition(parent, above, end))
    return null
  }

  return ReactDOM.createPortal(
    <ul
      ref={listRef}
      className={cl(styles.dropdown, className)}
      style={position}
      onMouseDown={onMouseDown}
    >
      {children}
    </ul>,
    portal
  )
}

type DropdownOptionsProps<T> = {
  above?: boolean
  parent: Element
  className?: string
  options: T[]
  children: (s: T[], f: number) => React.ReactNode
  onChange: (option: T) => void
  onFocus?: (option: T) => void
}

export function DropdownOptions<T>({
  above,
  parent,
  options,
  className,
  children,
  onChange,
  onFocus,
  ...props
}: DropdownOptionsProps<T>) {
  const list = useRef<HTMLUListElement>(null)
  const [focused, setFocus] = useState(0)

  useKeyboardControls(
    list.current,
    focused,
    options,
    setFocus,
    onChange,
    onFocus
  )

  return (
    <Dropdown
      {...props}
      listRef={list}
      above={above}
      parent={parent}
      className={cl(styles.dropdownOptions, className)}
    >
      {children(options, focused)}
    </Dropdown>
  )
}
