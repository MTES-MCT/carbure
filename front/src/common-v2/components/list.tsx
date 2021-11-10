import React, { useCallback, useEffect, useRef, useState } from "react"
import cl from "clsx"
import { isInside } from "./dropdown"
import css from "./list.module.css"
import {
  defaultFilter,
  defaultNormalizer,
  Filter,
  listTreeItems,
  Normalized,
  NormalizedTree,
  Normalizer,
  normalizeTree,
} from "../hooks/normalize"
import { SearchInput } from "./input"
import { multipleSelection, singleSelection } from "../hooks/selection"

export interface ListProps<T> {
  controlRef?: React.RefObject<HTMLElement>
  items: T[]
  search?: boolean
  striped?: boolean
  multiple?: boolean
  selectedItem?: T
  selectedItems?: T[]
  className?: string
  style?: React.CSSProperties
  onFocus?: (item: T | undefined) => void
  onSelectItem?: (item: T | undefined) => void
  onSelectItems?: (items: T[]) => void
  normalize?: Normalizer<T>
  filter?: Filter<T>
  children?: Renderer<T>
}

export function List<T>({
  search,
  striped,
  items,
  multiple = false,
  controlRef,
  selectedItem,
  selectedItems,
  className,
  style,
  onFocus,
  onSelectItem,
  onSelectItems,
  filter = defaultFilter,
  normalize = defaultNormalizer,
  children: render = defaultRenderer,
}: ListProps<T>) {
  const listRef = useRef<HTMLUListElement>(null)
  const [query, setQuery] = useState<string | undefined>()

  function filterItem(item: NormalizedTree<T>) {
    const ilabel = item.label.toLowerCase()
    const iquery = query?.toLowerCase() ?? ""
    return filter(item) && ilabel.includes(iquery)
  }

  const normItems = normalizeTree(items, normalize, filterItem)

  const selection = useSelection({
    items: normItems,
    container: listRef.current,
    multiple,
    selectedItem,
    selectedItems,
    onFocus,
    onSelectItem,
    onSelectItems,
    normalize,
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

  // prettier-ignore
  const onExit = useCallback((e: FocusEvent | React.FocusEvent | MouseEvent | React.MouseEvent) => {
    if (!isInside(e.currentTarget, e.relatedTarget)) {
      selection.clear();
    }
  }, [selection])

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

  function renderItems(items: NormalizedTree<T>[], level: number = 0) {
    if (items.length === 0) {
      return <li>Aucune entrée trouvée</li>
    }

    return items.map(({ key, label, children, disabled, value }, i) => {
      const config: ItemConfig<T> = {
        key,
        label,
        value,
        level,
        disabled,
        group: Boolean(children),
        selected: selection.isSelected(value),
        focused: selection.isFocused(value),
      }

      // render group header
      if (children) {
        return (
          <div key={key ?? i}>
            <li
              data-group
              data-key={key}
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
          key={key ?? i}
          data-key={key}
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
        <SearchInput clear variant="inline" value={query} onChange={setQuery} />
      )}
      {renderItems(normItems)}
    </ul>
  )
}

export interface ItemConfig<T> extends Normalized<T> {
  level: number
  selected: boolean
  focused: boolean
  group: boolean
}

export type Renderer<T> = (config: ItemConfig<T>) => React.ReactNode
export const defaultRenderer: Renderer<any> = (config) => config.label

export interface SelectionConfig<T> {
  items: NormalizedTree<T>[]
  container: HTMLElement | null
  multiple?: boolean
  selectedItem?: T
  selectedItems?: T[]
  onFocus?: (item: T | undefined) => void
  onSelectItem?: (item: T | undefined) => void
  onSelectItems?: (items: T[]) => void
  normalize?: Normalizer<T>
}

export function useSelection<T>({
  items,
  container,
  multiple,
  selectedItem,
  selectedItems,
  onFocus,
  onSelectItem,
  onSelectItems,
  normalize = defaultNormalizer,
}: SelectionConfig<T>) {
  const [focused, setFocused] = useState<T | undefined>(selectedItem)

  useEffect(() => {
    setFocused(selectedItem)
  }, [selectedItem])

  const normItems = listTreeItems(items)
  const normFocus = focused && { value: focused, ...normalize(focused) }

  const { isSelected, onSelect } = multiple
    ? multipleSelection(selectedItems, onSelectItems, normalize)
    : singleSelection(selectedItem, onSelectItem, normalize)

  function isFocused(item: T) {
    return normalize(item).key === normFocus?.key
  }

  function index() {
    return normItems.findIndex((item) => item.key === normFocus?.key)
  }

  function prev() {
    const i = index()
    const prev = i === -1 ? normItems.length - 1 : Math.max(i - 1, 0)
    const item = normItems[prev]
    scrollToKey(container, item?.key)
    setFocused(item?.value)
    onFocus?.(item?.value)
  }

  function next() {
    const i = index()
    const next = i === -1 ? 0 : Math.min(i + 1, normItems.length - 1)
    const item = normItems[next]
    scrollToKey(container, item?.key)
    setFocused(item?.value)
    onFocus?.(item?.value)
  }

  function select(item: T | undefined = focused) {
    onSelect(item)
    setFocused(item)
  }

  function clear() {
    setFocused(undefined)
  }

  function focus(item: T | undefined) {
    setFocused(item)
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

export default List
