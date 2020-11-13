import React, {
  CSSProperties,
  useCallback,
  useEffect,
  useRef,
  useState,
} from "react"
import ReactDOM from "react-dom"
import cl from "clsx"

import { LabelInput, LabelInputProps } from "."

import styles from "./autocomplete.module.css"

import { useDropdown } from "./dropdown"
import useAPI from "../../hooks/helpers/use-api"

const portal = document.getElementById("modal")!

type SuggestionsProps<T> = {
  suggestions: T[]
  parent: HTMLDivElement | null
  getValue: (option: T) => string
  getLabel: (option: T) => string
  onFocus: (option: T) => void
  onChange: (option: T) => void
}

function Suggestions<T>({
  suggestions,
  parent,
  getValue,
  getLabel,
  onFocus,
  onChange,
}: SuggestionsProps<T>) {
  const list = useRef<HTMLUListElement>(null)
  const [focused, setFocused] = useState(0)
  const [position, setPosition] = useState<CSSProperties | null>(null)

  function scrollTo(index: number) {
    if (list.current !== null) {
      const li = list.current.children[index]
      li.scrollIntoView({ block: "nearest", inline: "nearest" })
    }
  }

  const updatePosition = useCallback(() => {
    if (parent !== null) {
      const bbox = parent.getBoundingClientRect()

      setPosition({
        top: bbox.top + bbox.height,
        left: bbox.left,
        minWidth: bbox.width,
      })
    }
  }, [parent])

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      // move up
      if (e.key === "ArrowUp") {
        e.preventDefault()

        const prev = Math.max(0, focused - 1)
        onFocus(suggestions[prev])
        scrollTo(prev)
        setFocused(prev)
      }
      // move down
      else if (e.key === "ArrowDown") {
        e.preventDefault()

        const next = Math.min(focused + 1, suggestions.length - 1)
        onFocus(suggestions[next])
        scrollTo(next)
        setFocused(next)
      }
      // select focused option
      else if (e.key === "Enter") {
        e.preventDefault()
        onChange(suggestions[focused])
      }
    }

    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [suggestions, focused])

  // dumb polling to reposition the suggestions in case of scrolling
  useEffect(() => {
    const interval = setInterval(updatePosition, 100)
    return () => clearInterval(interval)
  }, [updatePosition])

  if (parent === null) {
    return null
  }

  if (position === null) {
    updatePosition()
    return null
  }

  return ReactDOM.createPortal(
    <ul ref={list} className={styles.suggestions} style={position}>
      {suggestions.map((option, i) => (
        <li
          key={getValue(option)}
          onClick={() => onChange(option)}
          className={cl(focused === i && styles.focusedSuggestion)}
        >
          {getLabel(option)}
        </li>
      ))}
    </ul>,
    portal
  )
}

function useAutoComplete<T>(
  value: T,
  name: string,
  queryArgs: any[],
  onChange: (e: any) => void,
  getLabel: (option: T) => string,
  getQuery: (q: string, ...a: any[]) => Promise<T[]>
) {
  const dd = useDropdown()

  const [query, setQuery] = useState(getLabel(value))
  const [suggestions, resolveQuery] = useAPI(getQuery)

  // on change, modify the query to match selection and send event to parent
  function change(value: T) {
    setQuery(getLabel(value))
    onChange({ target: { name, value } })
    dd.toggle(false)
  }

  function onQuery(e: React.ChangeEvent<HTMLInputElement>) {
    const query = e.target.value
    setQuery(query)

    if (query.length === 0) {
      dd.toggle(false)
    } else {
      dd.toggle(true)
      resolveQuery(query, ...queryArgs)
    }
  }

  // modify input content when passed value is changed
  useEffect(() => {
    setQuery(getLabel(value))
  }, [value, getLabel])

  return { dd, query, suggestions, onQuery, change }
}

type AutoCompleteProps<T> = Omit<LabelInputProps, "value"> & {
  value: T
  options?: T[]
  queryArgs?: any[]
  getValue: (option: T) => string
  getLabel: (option: T) => string
  onChange: (e: any) => void
  getQuery: (q: string, ...a: any[]) => Promise<T[]>
}

function AutoComplete<T>({
  value,
  name,
  queryArgs = [],
  readOnly,
  onChange,
  getValue,
  getLabel,
  getQuery,
  ...props
}: AutoCompleteProps<T>) {
  const container = useRef<HTMLDivElement>(null)

  const { dd, query, suggestions, onQuery, change } = useAutoComplete(
    value,
    name!,
    queryArgs,
    onChange,
    getLabel,
    getQuery
  )

  const isEmpty = !suggestions.data || suggestions.data.length === 0

  return (
    <div ref={container}>
      <LabelInput
        {...props}
        value={query}
        readOnly={readOnly}
        onChange={onQuery}
      />

      {!readOnly && !isEmpty && dd.isOpen && (
        <Suggestions
          suggestions={suggestions.data!}
          getValue={getValue}
          getLabel={getLabel}
          onFocus={() => {}}
          onChange={change}
          parent={container.current}
        />
      )}
    </div>
  )
}

export default AutoComplete
