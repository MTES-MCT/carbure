import cl from "clsx"
import { ReactNode, useRef, useState } from "react"
import { Normalizer, Sorter } from "../utils/normalize"
import Dropdown, { Trigger } from "./dropdown"
import { Control } from "./input"
import css from "./tooltip.module.css"

export interface TooltipProps<T, V = T> extends Control, Trigger {
  children: ReactNode
  title: string
  value?: V | undefined
  options?: T[]
  defaultOptions?: T[]
  getOptions?: (query: string) => Promise<T[]>
  onChange?: (value: V | undefined) => void
  onQuery?: (query: string) => void
  create?: (value: string) => V
  normalize?: Normalizer<T, V>
  sort?: Sorter<T, V>
}

function Tooltip<T, V>({ children, title, style }: TooltipProps<T, V>) {
  const triggerRef = useRef<HTMLInputElement>(null)
  const [isOpen, setIsOpen] = useState<boolean>()
  return (
    <>
      <div ref={triggerRef}>
        {isOpen && <div className={cl(css.arrow)} style={{}}></div>}
        {children}
      </div>
      <Dropdown
        openOnHover={true}
        triggerRef={triggerRef}
        anchor="top start"
        className={cl(css.dropdown)}
        onOpen={() => setIsOpen(true)}
        onClose={() => setIsOpen(false)}
      >
        <div className={cl(css.tooltip)}>{title}</div>
      </Dropdown>
    </>
  )
}

export default Tooltip
