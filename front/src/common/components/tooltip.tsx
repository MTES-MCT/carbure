import { useAsyncList } from "common/hooks/async-list"
import { matches } from "common/utils/collection"
import { ReactNode, useEffect, useRef, useState } from "react"
import cl from "clsx"
import css from "./tooltip.module.css"
import {
  defaultNormalizer,
  Normalizer,
  normalizeItems,
  denormalizeItems,
  Sorter,
} from "../utils/normalize"
import Dropdown, { Trigger } from "./dropdown"
import { Control, TextInput } from "./input"
import List, { createQueryFilter, defaultRenderer, Renderer } from "./list"

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

function Tooltip<T, V>({
  children,
  title,
  loading,
  value,
  options,
  defaultOptions,
  getOptions,
  onChange,
  onQuery,
  create,
  anchor,
  normalize = defaultNormalizer,
  sort,
  ...props
}: TooltipProps<T, V>) {
  const triggerRef = useRef<HTMLInputElement>(null)

  return (
    <>
      <div title={title} ref={triggerRef}>
        {children}
      </div>

      <Dropdown
        openOnHover={true}
        triggerRef={triggerRef}
        anchor="top start"
        className={cl(css.toolip_dropdown)}
      >
        <div className={cl(css.tooltip)}>{title}</div>
      </Dropdown>
    </>
  )
}

export default Tooltip
