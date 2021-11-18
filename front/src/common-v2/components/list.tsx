import React, { useCallback, useEffect, useRef, useState } from "react"
import cl from "clsx"
import { isInside } from "./dropdown"
import { multipleSelection, singleSelection } from "../utils/selection"
import { standardize } from "../utils/formatters"
import {
  defaultFilter,
  defaultNormalizer,
  Filter,
  listTreeItems,
  Normalized,
  Normalizer,
  normalizeItems,
} from "../utils/normalize"
import { SearchInput } from "./input"
import css from "./list.module.css"

export interface ListProps<T, V> {
  controlRef?: React.RefObject<HTMLElement>
  items: T[]
  search?: boolean
  striped?: boolean
  multiple?: boolean
  selectedValue?: V
  selectedValues?: V[]
  className?: string
  style?: React.CSSProperties
  onFocus?: (key: V | undefined) => void
  onSelectValue?: (key: V | undefined) => void
  onSelectValues?: (keys: V[]) => void
  normalize?: Normalizer<T, V>
  filter?: Filter<T, V>
  children?: Renderer<T, V>
}

export function List<T, V>({
  search,
  striped,
  items,
  multiple = false,
  controlRef,
  selectedValue,
  selectedValues,
  className,
  style,
  onFocus,
  onSelectValue,
  onSelectValues,
  filter = defaultFilter,
  normalize = defaultNormalizer,
  children: render = defaultRenderer,
}: ListProps<T, V>) {
  const listRef = useRef<HTMLUListElement>(null)
  const [query, setQuery] = useState<string | undefined>()

  const queryFilter = createQueryFilter(query ?? "")
  function filterItem(item: Normalized<T, V>) {
    return filter(item) && queryFilter(item)
  }

  const normItems = normalizeItems(items, normalize, filterItem)

  const selection = useSelection({
    items: normItems,
    container: listRef.current,
    multiple,
    selectedValue,
    selectedValues,
    onFocus,
    onSelectValue,
    onSelectValues,
  })

  const onKeyDown = useCallback(
    (e: KeyboardEvent | React.KeyboardEvent) => {
      switch (e.key) {
        case "ArrowUp":
          e.preventDefault()
          return selection.prev()

        case "ArrowDown":
          e.preventDefault()
          return selection.next()

        case "Enter":
          e.preventDefault()
          return selection.select()
      }
    },
    [selection]
  )

  const onExit = useCallback(
    (e: FocusEvent | React.FocusEvent | MouseEvent | React.MouseEvent) => {
      if (!isInside(e.currentTarget, e.relatedTarget)) {
        selection.clear()
      }
    },
    [selection]
  )

  useEffect(() => {
    const control = controlRef?.current
    if (!control) return

    control.addEventListener("keydown", onKeyDown)
    control.addEventListener("blur", onExit)
    control.addEventListener("mouseout", onExit)

    return () => {
      control.removeEventListener("keydown", onKeyDown)
      control.removeEventListener("blur", onExit)
      control.removeEventListener("mouseout", onExit)
    }
  }, [selection, controlRef, onExit, onKeyDown])

  function renderItems(items: Normalized<T, V>[], level: number = 0) {
    if (items.length === 0) {
      return <li>Aucune entrée trouvée</li>
    }

    return items.map(({ key, value, label, children, disabled, data }) => {
      const config: ItemConfig<T, V> = {
        key,
        value,
        label,
        level,
        disabled,
        data,
        group: Boolean(children),
        selected: selection.isSelected(value),
        focused: selection.isFocused(value),
      }

      // do not render group with no children
      if (children && children.length === 0) {
        return null
      }

      // render group header
      if (children) {
        return (
          <div key={label}>
            <li
              data-group
              data-key={label}
              data-disabled={disabled ? true : undefined}
              data-level={level > 0 ? level : undefined}
              data-selected={config.selected ? true : undefined}
              data-focused={config.focused ? true : undefined}
              onMouseOver={!disabled ? () => selection.focus(value) : undefined}
              onClick={!disabled ? () => selection.select(value) : undefined}
            >
              {render(config)}
            </li>
            <ul>{renderItems(children, level + 1)}</ul>
          </div>
        )
      }

      // render item
      return (
        <li
          key={label}
          data-key={label}
          data-disabled={disabled ? true : undefined}
          data-level={level > 0 ? level : undefined}
          data-selected={config.selected ? true : undefined}
          data-focused={config.focused ? true : undefined}
          onMouseOver={!disabled ? () => selection.focus(value) : undefined}
          onClick={!disabled ? () => selection.select(value) : undefined}
        >
          {render(config)}
        </li>
      )
    })
  }

  return (
    <ul
      data-list
      ref={listRef}
      tabIndex={0}
      className={cl(css.list, striped && css.striped, className)}
      style={style}
      onMouseOut={onExit}
      onBlur={onExit}
      onKeyDown={onKeyDown}
    >
      {search && (
        <SearchInput
          clear={true}
          variant="inline"
          value={query}
          onChange={setQuery}
        />
      )}
      {renderItems(normItems)}
    </ul>
  )
}

export interface ItemConfig<T, V> extends Normalized<T, V> {
  level: number
  selected: boolean
  focused: boolean
  group: boolean
}

export type Renderer<T, V> = (config: ItemConfig<T, V>) => React.ReactNode
export const defaultRenderer: Renderer<any, any> = (config) => config.label

export interface SelectionConfig<T, V> {
  items: Normalized<T, V>[]
  container: HTMLElement | null
  multiple?: boolean
  selectedValue?: V
  selectedValues?: V[]
  onFocus?: (value: V | undefined) => void
  onSelectValue?: (value: V | undefined) => void
  onSelectValues?: (values: V[]) => void
}

export function useSelection<T, V>({
  items,
  container,
  multiple,
  selectedValue,
  selectedValues,
  onFocus,
  onSelectValue,
  onSelectValues,
}: SelectionConfig<T, V>) {
  const [focused, focus] = useState<V | undefined>(selectedValue)

  useEffect(() => {
    focus(selectedValue)
  }, [selectedValue])

  const normItems = listTreeItems(items)
  const normFocus = normItems.find(
    (item) => item.key === JSON.stringify(focused)
  )

  const { isSelected, onSelect } = multiple
    ? multipleSelection(selectedValues, onSelectValues)
    : singleSelection(selectedValue, onSelectValue)

  function isFocused(value: V) {
    return JSON.stringify(value) === normFocus?.key
  }

  function index() {
    return normItems.findIndex((item) => item.key === normFocus?.key)
  }

  function prev() {
    const i = index()
    const prev = i === -1 ? normItems.length - 1 : Math.max(i - 1, 0)
    const item = normItems[prev]
    scrollToKey(container, item?.label)
    focus(item?.value)
    onFocus?.(item?.value)
  }

  function next() {
    const i = index()
    const next = i === -1 ? 0 : Math.min(i + 1, normItems.length - 1)
    const item = normItems[next]
    scrollToKey(container, item?.label)
    focus(item?.value)
    onFocus?.(item?.value)
  }

  function select(value: V | undefined = focused) {
    onSelect(value)
    focus(value)
  }

  function clear() {
    focus(undefined)
  }

  return { isFocused, isSelected, focus, prev, next, select, clear }
}

// scroll to option with given key
export function scrollToKey(
  container: HTMLElement | null,
  key: string | undefined
) {
  if (!container || !key) return
  const node = container.querySelector(`[data-key="${key}"]`)
  node?.scrollIntoView({ block: "nearest", inline: "nearest" })
}

export function createQueryFilter<T, V>(
  query: string,
  exact?: boolean
): Filter<T, V> {
  const stdQuery = standardize(query)
  return (item) => {
    const stdItem = standardize(item.label)
    return exact ? stdItem === stdQuery : stdItem.includes(stdQuery)
  }
}

export default List
